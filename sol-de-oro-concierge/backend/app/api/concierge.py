import json
import logging
import re

from fastapi import APIRouter
from pydantic import BaseModel

from app.llm.nvidia_client import chat
from app.session import append_message, get_session
from app.tools import supabase as tools

logger = logging.getLogger(__name__)
router = APIRouter()

_TOOLS_SPEC = [
    {"type": "function", "function": {"name": "get_rooms", "description": "Lista las 9 categorías de habitaciones del hotel con sus specs completas (tamaño, cama, vista, capacidad, amenidades).", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_salons", "description": "Lista los salones de eventos del hotel, opcionalmente filtrados por capacidad mínima de personas.", "parameters": {"type": "object", "properties": {"min_pax": {"type": "integer", "description": "Capacidad mínima requerida en personas"}}}}},
    {"type": "function", "function": {"name": "get_faq", "description": "Busca preguntas frecuentes sobre políticas, instalaciones y servicios del hotel (check-in, mascotas, tarjetas, cancelación, voltaje, moneda, idiomas, piscina, gimnasio, spa, wifi, desayuno, room service, etc.), opcionalmente filtradas por tema.", "parameters": {"type": "object", "properties": {"topic": {"type": "string", "description": "Palabra clave del tema, ej: 'mascota', 'check-in', 'voltaje', 'piscina'"}}}}},
    {"type": "function", "function": {"name": "get_nearby", "description": "Lista lugares y actividades cerca del hotel (En el hotel, Compras, Costa, Paseos, Empresarial), opcionalmente filtrados por categoría.", "parameters": {"type": "object", "properties": {"cat": {"type": "string", "enum": ["hotel", "shopping", "coast", "paseos", "business"]}}}}},
    {"type": "function", "function": {"name": "get_restaurants", "description": "Lista los restaurantes recomendados cerca del hotel.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_cultural", "description": "Lista los lugares culturales recomendados cerca del hotel (museos, sitios históricos).", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_offers", "description": "Lista las ofertas y promociones vigentes del hotel.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_contact_info", "description": "Devuelve los canales de contacto del hotel: link para reservar habitación (iHotelier), email y teléfono de reservas, teléfono de recepción, y el email/teléfono/WhatsApp para cotizar eventos.", "parameters": {"type": "object", "properties": {}}}},
]


def _get_contact_info(**kw) -> dict:
    return {
        "booking_url": "https://soldeoro.ihotelier.com/es/book/dates-of-stay",
        "reservations_email": "reservas@soldeoro.pe",
        "reservations_phone": "+51 988 861 380",
        "front_desk_phone": "+51 (1) 610-7000",
        "events_email": "comercial@soldeoro.pe",
        "events_phone": "+51 988 861 380",
        "whatsapp": "https://wa.link/dc0dft",
    }


_TOOL_FUNCS = {
    "get_rooms": lambda **kw: tools.get_rooms(),
    "get_salons": lambda **kw: tools.get_salons(min_pax=kw.get("min_pax")),
    "get_faq": lambda **kw: tools.get_faq(topic=kw.get("topic")),
    "get_nearby": lambda **kw: tools.get_nearby(cat=kw.get("cat")),
    "get_restaurants": lambda **kw: tools.get_restaurants(),
    "get_cultural": lambda **kw: tools.get_cultural(),
    "get_offers": lambda **kw: tools.get_offers(),
    "get_contact_info": lambda **kw: _get_contact_info(),
}

_SYSTEM_PROMPT = (
    "Eres el Concierge digital del hotel Sol de Oro (Miraflores, Lima, Calle San Martín 305). "
    "Respondes corto, claro, elegante y orientado a acción, como un concierge de hotel 5 estrellas — "
    "nunca como un chatbot genérico. Máximo 3-4 frases por respuesta. Cuando una herramienta te "
    "devuelva varias opciones (habitaciones, salones, lugares), NO las describas todas en detalle "
    "— pero SIEMPRE menciona el nombre real de al menos 2 o 3 (nunca respondas solo con preguntas "
    "genéricas sin nombrar ninguna opción concreta), con su dato clave (capacidad, tamaño o "
    "distancia), y después pregunta qué le interesa más al huésped para profundizar ahí. Nunca "
    "dejes una frase a medias: si vas a listar varias opciones, sé breve para que la respuesta "
    "completa quepa cómoda.\n\n"
    "Usa SIEMPRE las herramientas disponibles para obtener datos reales antes de responder sobre "
    "habitaciones, salones, políticas, instalaciones, lugares cercanos, restaurantes, cultura u ofertas. "
    "Nunca inventes precios, disponibilidad, horarios, capacidades, distancias o medios de transporte que "
    "no estén en los datos devueltos por las herramientas. Cuando los datos incluyan una cifra concreta "
    "(m², minutos, capacidad, hora), inclúyela siempre en tu respuesta — no la resumas de forma vaga.\n\n"
    "ÚNICOS canales de contacto reales del hotel — NUNCA menciones un sitio web, teléfono, email o link "
    "distinto a estos, aunque te parezca razonable inventarlo para sonar útil. Si no estás seguro de un "
    "dato de contacto, usa exactamente estos o no lo menciones:\n"
    "- Reservar habitación: https://soldeoro.ihotelier.com/es/book/dates-of-stay\n"
    "- Reservas: reservas@soldeoro.pe · +51 988 861 380\n"
    "- Recepción: +51 (1) 610-7000\n"
    "- Eventos / cotizaciones: comercial@soldeoro.pe · +51 988 861 380 · WhatsApp https://wa.link/dc0dft\n"
    "Cuando el huésped quiera reservar una habitación, cotizar un evento, o contactar al hotel por "
    "cualquier motivo, dale el canal correspondiente de la lista de arriba directamente en la misma "
    "respuesta — no le pidas más detalles antes de dar el dato de contacto o el link de reserva. Puedes "
    "usar get_contact_info si necesitas confirmar estos datos, pero no es obligatorio ya que están arriba.\n\n"
    "Sobre lugares cercanos: la categoría \"hotel\" de get_nearby es solo para instalaciones DENTRO del "
    "hotel (piscina, gimnasio, spa) — úsala para preguntas sobre instalaciones o servicios del hotel. "
    "Para \"qué hacer cerca / afuera del hotel\" en general, considera varias categorías (compras, costa, "
    "paseos) y elige las que mejor calcen con el pedido (pareja o romántico → costa, ej. Malecón o Parque "
    "del Amor; poco tiempo disponible → lo más cercano en minutos; primera vez en Lima → una mezcla variada).\n\n"
    "Si no tienes el dato, dilo y sugiere contactar al hotel directamente."
)


class ConciergeRequest(BaseModel):
    message: str
    session_id: str


class ConciergeResponse(BaseModel):
    message: str
    intent: str
    actions: list[dict]


_FALLBACK_MESSAGE = "Dame un momento, tengo un problema técnico para responder eso. Te recomiendo contactar directamente al hotel."
_CONTACT_ACTION = {"type": "CONTACT_HOTEL", "label": "Contactar hotel", "url": "mailto:reservas@soldeoro.pe"}

# Salvaguarda determinística contra alucinación de contacto: en pruebas manuales el modelo
# inventó dominios/teléfonos falsos ("hotelsoldemiraflores.com", "+51 1 242 1234") a pesar de
# que el system prompt ya trae los datos reales — el prompt engineering solo no bastó para
# garantizar esto de forma confiable con un modelo de 8B. Esta función es el guardrail en
# código: nunca se le muestra al huésped un email/teléfono/link de contacto que no sea real.
_ALLOWED_EMAILS = {"reservas@soldeoro.pe", "comercial@soldeoro.pe"}
_ALLOWED_URL_DOMAINS = ("soldeoro.pe", "soldeoro.ihotelier.com", "wa.link")
_ALLOWED_PHONE_DIGITS = {"5116107000", "51988861380"}  # +51 (1) 610-7000 · +51 988 861 380

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_URL_RE = re.compile(r"https?://[^\s\)\]]+")
_PHONE_RE = re.compile(r"\+?51[\s\-]?\(?\d\)?[\s\-\d]{6,}\d")

_REAL_CONTACT_LINE = (
    "Reservar habitación: https://soldeoro.ihotelier.com/es/book/dates-of-stay · "
    "Contacto: reservas@soldeoro.pe · +51 (1) 610-7000"
)


def _scrub_fabricated_contact(text: str) -> str:
    fabricated = False

    def _check_email(m: re.Match) -> str:
        nonlocal fabricated
        if m.group(0) in _ALLOWED_EMAILS:
            return m.group(0)
        fabricated = True
        return ""

    def _check_url(m: re.Match) -> str:
        nonlocal fabricated
        if any(domain in m.group(0) for domain in _ALLOWED_URL_DOMAINS):
            return m.group(0)
        fabricated = True
        return ""

    def _check_phone(m: re.Match) -> str:
        nonlocal fabricated
        digits = re.sub(r"\D", "", m.group(0))
        if digits in _ALLOWED_PHONE_DIGITS:
            return m.group(0)
        fabricated = True
        return ""

    text = _EMAIL_RE.sub(_check_email, text)
    text = _URL_RE.sub(_check_url, text)
    text = _PHONE_RE.sub(_check_phone, text)

    if fabricated:
        text = text.rstrip() + "\n\n" + _REAL_CONTACT_LINE
    return text


@router.post("/api/concierge", response_model=ConciergeResponse)
def concierge(payload: ConciergeRequest) -> ConciergeResponse:
    append_message(payload.session_id, "user", payload.message)
    session = get_session(payload.session_id)

    messages = [{"role": "system", "content": _SYSTEM_PROMPT}, *session["history"]]

    try:
        result = chat(messages=messages, tools=_TOOLS_SPEC)

        if result["tool_calls"]:
            messages.append({"role": "assistant", "content": result["content"] or "", "tool_calls": [
                {"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": tc["arguments"]}}
                for tc in result["tool_calls"]
            ]})
            for tc in result["tool_calls"]:
                try:
                    args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                except json.JSONDecodeError:
                    # El modelo a veces devuelve JSON de argumentos mal formado (no-determinismo,
                    # temperature > 0) — se trata como "sin argumentos" en vez de tumbar el request.
                    args = {}
                # Errores de Supabase (timeout, 5xx) se propagan y caen en el except de abajo —
                # nunca se inventa el dato faltante, se cae al mensaje de fallback (spec, "Manejo de errores").
                tool_fn = _TOOL_FUNCS.get(tc["name"])
                if tool_fn is None:
                    # El modelo puede alucinar un nombre de tool que no declaramos — se devuelve un
                    # error legible en el mensaje "tool" para que el modelo se recupere en la siguiente
                    # llamada en vez de tumbar el request entero.
                    tool_result = {"error": f"herramienta desconocida: {tc['name']}"}
                else:
                    tool_result = tool_fn(**args)
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": json.dumps(tool_result, ensure_ascii=False)})
            result = chat(messages=messages)

        final_message = _scrub_fabricated_contact(result["content"]) if result["content"] else _FALLBACK_MESSAGE
        actions = [] if result["content"] else [_CONTACT_ACTION]
    except Exception:
        # Captura fallos de NVIDIA Build (rate limit, timeout, modelo caído) y de Supabase
        # (tool call fallido). Nunca se propaga un 500 crudo al widget ni se inventa contenido.
        # Se loguea server-side para poder diagnosticar fallas intermitentes del modelo sin
        # exponer detalles internos en la respuesta al huésped.
        logger.exception("Fallo al procesar mensaje del concierge (session_id=%s)", payload.session_id)
        final_message = _FALLBACK_MESSAGE
        actions = [_CONTACT_ACTION]

    append_message(payload.session_id, "assistant", final_message)
    return ConciergeResponse(message=final_message, intent="UNCLASSIFIED", actions=actions)
