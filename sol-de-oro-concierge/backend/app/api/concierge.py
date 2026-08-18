import json
import logging
import re
import urllib.parse

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.llm.nvidia_client import chat, chat_stream
from app.session import append_message, get_session
from app.tools import supabase as tools

logger = logging.getLogger(__name__)
router = APIRouter()

_TOOLS_SPEC = [
    {"type": "function", "function": {"name": "get_rooms", "description": "Lista las 9 categorías de habitaciones del hotel con sus specs completas (tamaño, cama, vista, capacidad, amenidades).", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_faq", "description": "Busca preguntas frecuentes sobre políticas, instalaciones y servicios del hotel (check-in, mascotas, tarjetas, cancelación, voltaje, moneda, idiomas, piscina, gimnasio, spa, wifi, desayuno, room service, restaurante del hotel, etc.), opcionalmente filtradas por tema.", "parameters": {"type": "object", "properties": {"topic": {"type": "string", "description": "Palabra clave del tema, ej: 'mascota', 'check-in', 'voltaje', 'piscina', 'restaurante'"}}}}},
    {"type": "function", "function": {"name": "get_nearby", "description": "Lista lugares, miradores, playas, faros y actividades cerca del hotel, agrupados en 5 categorías: hotel (piscina/gimnasio/spa, dentro del hotel), shopping (Larcomar, Parque Kennedy, Av. Larco, Mercado Indio), coast (Malecón, Parque del Amor, Faro de la Marina, Parque María Reiche, Costa Verde, playas), paseos (Barranco, Puente de los Suspiros), business (zonas empresariales). Úsala para CUALQUIER lugar, mirador o punto de interés que no sea un museo/sitio arqueológico formal ni un restaurante.", "parameters": {"type": "object", "properties": {"cat": {"type": "string", "enum": ["hotel", "shopping", "coast", "paseos", "business"]}}}}},
    {"type": "function", "function": {"name": "get_restaurants", "description": "Lista los restaurantes recomendados CERCA del hotel (fuera del hotel, en Miraflores/Lima). Para el restaurante DEL hotel (Restaurante Murano) usa get_faq buscando el tema restaurante en su lugar.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_cultural", "description": "Lista SOLO museos y sitios arqueológicos/históricos formales con entrada y visita guiada (ej. Huaca Pucllana, museos). Para miradores, faros, parques o paseos usa get_nearby en vez de esta.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_offers", "description": "Lista las ofertas y promociones vigentes del hotel.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_contact_info", "description": "Devuelve los canales de contacto del hotel (link de reserva iHotelier, emails, teléfonos) y las URLs reales de las páginas principales del sitio (habitaciones, eventos, restaurante, servicios, experiencias, ofertas, FAQ) para armar links o CTAs.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_salons", "description": "Consulta si el hotel tiene espacios para eventos con capacidad suficiente para una cantidad de personas. Úsala cuando pregunten por salones, espacios para eventos, o te den un número de invitados/asistentes para un evento. Devuelve SOLO un resumen agregado de capacidad — nunca nombres de salones, pisos, montajes ni cifras de un salón individual. Para disponibilidad, montaje, precio o reservar el espacio, deriva siempre con get_whatsapp_handoff (topic='eventos').", "parameters": {"type": "object", "properties": {"guests": {"type": "integer", "description": "Cantidad aproximada de personas del evento, si el huésped ya la mencionó"}}}}},
    {"type": "function", "function": {"name": "capture_lead", "description": "Guarda de forma acumulativa los datos de contacto y de la consulta que el huésped te va dando durante la conversación (nombre, email, teléfono, empresa, tipo de evento, fecha, cantidad de personas, requerimientos). Llámala cada vez que el huésped te dé un dato nuevo de este tipo, así no se pierde y no hace falta volver a preguntarlo. No inventes ningún valor: solo pasa lo que el huésped realmente dijo.", "parameters": {"type": "object", "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"},
        "phone": {"type": "string"},
        "company": {"type": "string"},
        "lead_type": {"type": "string", "enum": ["habitaciones", "eventos", "restaurante", "general"]},
        "event_type": {"type": "string"},
        "event_date": {"type": "string", "description": "Fecha del evento tal como la dio el huésped, ej. '20 de septiembre'"},
        "guests": {"type": "integer"},
        "requirements": {"type": "string"},
    }}}},
    {"type": "function", "function": {"name": "get_whatsapp_handoff", "description": "Deriva la conversación a un humano del hotel por WhatsApp, con el contexto de la conversación (y los datos guardados con capture_lead, si los hay) ya incluidos en el mensaje pre-armado. Úsala SIEMPRE que: (a) el huésped quiera avanzar con disponibilidad, montaje, cotización o reservar un espacio para su evento (después de haber consultado get_salons para la capacidad); (b) el huésped pida explícitamente hablar con alguien del hotel o necesite ayuda personalizada; (c) tengas una solicitud que no puedas resolver del todo. Para una reserva de habitación simple, prefiere el link de iHotelier de get_contact_info en vez de esta herramienta. Parámetro topic obligatorio.", "parameters": {"type": "object", "properties": {"topic": {"type": "string", "enum": ["eventos", "reserva_habitacion", "general"]}}, "required": ["topic"]}}},
]

# Mapea cada site_section (el mismo texto que ya arma app/tools/supabase.py) a la URL REAL del
# sitio — nunca inventada, sacada de inspeccionar los anchors/IDs reales de cada página. Única
# fuente de verdad para "a dónde puede llevar el Concierge al huésped".
_SECTION_TO_URL = {
    "Habitaciones": "habitaciones.html#showcase",
    "Eventos": "eventos.html#salones",
    "Preguntas frecuentes (FAQ)": "faq.html",
    "Experiencias → En el Hotel": "experiencias.html",
    "Experiencias → Compras · Ocio": "experiencias.html",
    "Experiencias → Costa": "experiencias.html",
    "Experiencias → Paseos": "experiencias.html",
    "Experiencias → Empresarial": "experiencias.html",
    "Experiencias → Gastronomía": "experiencias.html",
    "Experiencias → Cultura": "experiencias.html",
    "Ofertas": "ofertas.html",
}
# Las FAQ traen su propia categoría (más específica que el site_section genérico "FAQ") — se
# usa para rutear a la página real cuando aplica (ej. una pregunta de "Habitaciones" en el FAQ
# lleva a habitaciones.html, no solo a faq.html).
_FAQ_CATEGORY_URL = {
    "Habitaciones": "habitaciones.html#showcase",
    "Servicios": "servicios.html#amenidades",
    "Eventos y reuniones": "eventos.html#salones",
}


def _add_site_url(rows: list[dict]) -> list[dict]:
    for row in rows:
        if row.get("category") in _FAQ_CATEGORY_URL:
            row["site_url"] = _FAQ_CATEGORY_URL[row["category"]]
        else:
            row["site_url"] = _SECTION_TO_URL.get(row.get("site_section"))
    return rows


def _get_contact_info(**kw) -> dict:
    return {
        "booking_url": "https://soldeoro.ihotelier.com/es/book/dates-of-stay",
        "rooms_reservations_email": "reservas@soldeoro.pe",
        "rooms_reservations_phone": "+51 (1) 610-7000",
        "restaurant_reservations_phone": "+51 (1) 610-7000",
        "events_email": "comercial@soldeoro.pe",
        # +51 924 664 487 es SOLO WhatsApp (no callable) — usa get_whatsapp_handoff para ese
        # canal. Este es el teléfono real para LLAMAR al equipo comercial.
        "events_phone": "+51 (1) 610-7000 anexo 8",
        "front_desk_lobby_phone": "+51 (1) 610-7000",
        # URLs reales de las páginas principales del sitio — para CTAs como "Ver habitaciones →"
        # cuando no hay una fila específica de una herramienta con su propio site_url.
        "rooms_page_url": "habitaciones.html#showcase",
        "events_page_url": "eventos.html#salones",
        "restaurant_page_url": "restaurante.html#carta",
        "services_page_url": "servicios.html#amenidades",
        "experiences_page_url": "experiencias.html",
        "offers_page_url": "ofertas.html",
        "faq_page_url": "faq.html",
    }


# El LLM nunca ve los salones fila por fila: solo un resumen agregado de capacidad. Esta es
# la garantía real de "nunca menciones nombres de salones" — vive en código, no solo en el
# prompt, siguiendo el mismo principio que _build_whatsapp_message (un 8B no es confiable
# solo con instrucciones de prompt para omitir datos que sí tiene delante).
def _get_salons_summary(**kw) -> dict:
    guests = kw.get("guests")
    if isinstance(guests, str) and guests.strip().isdigit():
        guests = int(guests)
    elif not isinstance(guests, int):
        guests = None
    salons = tools.get_salons()
    capacities = [s["capacity_max"] for s in salons if s.get("capacity_max")]
    matching_count = sum(1 for c in capacities if guests is None or c >= guests)
    return {
        "has_event_spaces": bool(salons),
        "requested_guests": guests,
        "capacity_covers_request": True if guests is None else matching_count > 0,
        "matching_alternatives_count": matching_count,
        "max_capacity_available": max(capacities) if capacities else 0,
        "site_url": "eventos.html#salones",
        "site_section": "Eventos",
    }


_TOOL_FUNCS = {
    "get_rooms": lambda **kw: _add_site_url(tools.get_rooms()),
    "get_faq": lambda **kw: _add_site_url(tools.get_faq(topic=kw.get("topic"))),
    "get_nearby": lambda **kw: _add_site_url(tools.get_nearby(cat=kw.get("cat"))),
    "get_restaurants": lambda **kw: _add_site_url(tools.get_restaurants()),
    "get_cultural": lambda **kw: _add_site_url(tools.get_cultural()),
    "get_offers": lambda **kw: _add_site_url(tools.get_offers()),
    "get_contact_info": lambda **kw: _get_contact_info(),
    "get_salons": lambda **kw: _get_salons_summary(**kw),
}

# Único número real de WhatsApp del hotel usado por el Concierge (confirmado por el usuario:
# se reutiliza para todo — eventos, reservas, consulta general — en vez de manejar varios
# números distintos). Nunca cambiar este valor sin instrucción explícita.
_WHATSAPP_BASE = "https://wa.me/51924664487"

_HANDOFF_TOPICS = {
    "eventos": {
        "intro": "Mi consulta sobre eventos",
        "email": "comercial@soldeoro.pe",
        # +51 924 664 487 es SOLO WhatsApp (no se puede llamar) — para una llamada real al
        # equipo comercial se usa el anexo del conmutador del hotel (eventos.html, panel de
        # contacto real de la página), no el número de WhatsApp.
        "phone": "+51 (1) 610-7000 anexo 8",
        "lead_in": "Para tu evento te conecto directo con nuestro equipo comercial, así lo atienden con el detalle exacto de tu consulta",
    },
    "reserva_habitacion": {
        "intro": "Quisiera consultar disponibilidad o reservar una habitación",
        "email": "reservas@soldeoro.pe",
        "phone": "+51 (1) 610-7000",
        "lead_in": "Te conecto directo con el equipo de reservas por WhatsApp, así coordinan tu estadía con el detalle exacto de tu consulta",
    },
    "general": {
        "intro": "Tengo una consulta",
        "email": "reservas@soldeoro.pe",
        "phone": "+51 (1) 610-7000",
        "lead_in": "Te conecto directo con el equipo del hotel por WhatsApp para que te atiendan con el detalle exacto de tu consulta",
    },
}


# CAPTURA DE LEADS: el modelo va acumulando datos de contacto/consulta con la tool
# capture_lead durante la conversación (en memoria, en session["lead"] — mismo modelo sin
# persistencia que el resto de session.py). Se escribe UNA sola fila en Supabase, en el
# momento del handoff a WhatsApp (ver _persist_lead) — es el punto natural donde ya sabemos
# que hay intención comercial, en vez de guardar una fila por cada pregunta general.
_LEAD_FIELDS = ("name", "email", "phone", "company", "lead_type", "event_type", "event_date", "guests", "requirements")
_LEAD_LABELS = {
    "name": "Nombre",
    "company": "Empresa",
    "event_type": "Tipo de evento",
    "event_date": "Fecha",
    "guests": "Asistentes",
    "requirements": "Requerimientos",
    "email": "Email",
    "phone": "Teléfono",
}


def _capture_lead(session: dict, args: dict) -> dict:
    lead = session.setdefault("lead", {})
    guests = args.get("guests")
    if isinstance(guests, str) and guests.strip().isdigit():
        args = {**args, "guests": int(guests)}
    for field in _LEAD_FIELDS:
        value = args.get(field)
        if value not in (None, ""):
            lead[field] = value
    return {"status": "guardado", "known_fields": {k: lead[k] for k in _LEAD_FIELDS if k in lead}}


def _format_lead_summary(lead: dict) -> str:
    lines = [f"{_LEAD_LABELS[k]}: {lead[k]}" for k in _LEAD_LABELS if lead.get(k)]
    return "\n".join(lines)


def _persist_lead(session: dict, session_id: str, topic: str) -> None:
    lead = session.get("lead")
    if not lead or lead.get("_persisted"):
        return
    payload = {
        "session_id": session_id,
        "lead_type": lead.get("lead_type") or topic,
        "status": "handoff_requested",
        "source": "ai_concierge",
        **{k: lead[k] for k in _LEAD_FIELDS if k not in ("lead_type",) and lead.get(k)},
    }
    try:
        tools.insert_lead(payload)
        lead["_persisted"] = True
    except Exception:
        # Igual que el resto de las tools: un fallo de Supabase nunca debe tumbar el handoff
        # ni el mensaje al huésped — el lead simplemente no queda guardado esta vez.
        logger.exception("Fallo al guardar lead del concierge (session_id=%s)", session_id)


# Deriva a un humano por WhatsApp en vez de dejar que el modelo enumere datos o intente
# resolverlo todo solo — arma un link con el contexto real de la conversación (mensajes del
# huésped hasta ahora) más el resumen estructurado del lead si existe, ya URL-encodeado, para
# que el equipo del hotel reciba la consulta lista para procesar. Un solo número real
# (_WHATSAPP_BASE) para los 3 topics, por decisión del cliente.
def _build_whatsapp_handoff(session: dict, topic: str, session_id: str) -> dict:
    cfg = _HANDOFF_TOPICS.get(topic, _HANDOFF_TOPICS["general"])
    history = session.get("history", [])
    lead = session.get("lead") or {}
    guest_messages = [m["content"] for m in history if m.get("role") == "user" and m.get("content")]
    context = " · ".join(guest_messages[-5:])
    if len(context) > 500:
        context = context[:500] + "..."
    lead_summary = _format_lead_summary(lead)
    if lead_summary:
        text = f"Hola, vengo del Concierge virtual de Sol de Oro. {cfg['intro']}.\n{lead_summary}\n\nDetalle de la conversación: {context}"
    else:
        text = f"Hola, vengo del Concierge virtual de Sol de Oro. {cfg['intro']}: {context}"
    encoded = urllib.parse.quote(text, safe="")
    _persist_lead(session, session_id, topic)
    return {
        "whatsapp_link": f"{_WHATSAPP_BASE}?text={encoded}",
        "contact_email": cfg["email"],
        "contact_phone": cfg["phone"],
        "lead_in": cfg["lead_in"],
        "site_section": "Contacto directo por WhatsApp",
    }


def _build_whatsapp_message(handoff: dict) -> str:
    # El link trae texto URL-encodeado (%20, %C3%B3...) — un modelo de 8B no lo reproduce de
    # forma confiable en prosa libre (se vio en pruebas: lo trunca o mezcla fragmentos
    # codificados con su propio texto). Se arma en código, igual que el resto de la
    # salvaguarda de contacto, en vez de confiar en el LLM para este paso puntual.
    return (
        f"{handoff['lead_in']}: [**Hablar con el hotel por WhatsApp →**]({handoff['whatsapp_link']})\n\n"
        f"También puedes escribir a {handoff['contact_email']} o llamar al {handoff['contact_phone']}."
    )


# PERSONAS: 3 concierges rotan al azar por sesión (mismo hotel, mismas reglas y datos —
# solo cambia el nombre y un matiz de personalidad, por pedido explícito: "hablando con algún
# toque diferente pero en sí similar"). El frontend elige la persona una vez por sesión nueva
# y la manda en cada request; el backend arma el prompt con ese nombre y ese matiz.
_PERSONAS = {
    "maria_paz": {
        "name": "María Paz",
        "flavor": "Tu estilo es cálido y detallista, como una anfitriona clásica que cuida cada palabra.",
    },
    "carlos": {
        "name": "Carlos",
        "flavor": "Tu estilo es directo y resolutivo: das la respuesta útil primero y vas al grano, sin perder la calidez.",
    },
    "claudia": {
        "name": "Claudia",
        "flavor": "Tu estilo es entusiasta y conversador: compartes recomendaciones con energía, sin perder la formalidad.",
    },
}
_DEFAULT_PERSONA_KEY = "maria_paz"


def _build_system_prompt(persona_key: str) -> str:
    persona = _PERSONAS.get(persona_key, _PERSONAS[_DEFAULT_PERSONA_KEY])
    return _SYSTEM_PROMPT_TEMPLATE.replace("{{NAME}}", persona["name"]).replace("{{FLAVOR}}", persona["flavor"])


_SYSTEM_PROMPT_TEMPLATE = (
    "Te llamas {{NAME}}, Concierge Virtual del hotel Sol de Oro (Miraflores, Lima, Calle San Martín "
    "305). Si el huésped pregunta tu nombre o quién eres, preséntate como {{NAME}}. Tu tono es amigable "
    "pero formal — cálido y cercano, nunca casual de más, como el trato de un concierge de hotel 5 "
    "estrellas, nunca como un chatbot genérico. {{FLAVOR}} Escribe como una persona real conversando, "
    "no como un párrafo corporativo: frases cortas y naturales, sin relleno ni repetir la pregunta del "
    "huésped antes de responder. Máximo 2-3 frases por respuesta cuando es una respuesta simple; si vas "
    "a presentar 2-3 opciones (habitaciones, experiencias, etc.) cada una puede tener su propio bloque "
    "corto — ver formato abajo.\n\n"
    "FORMATO — usa markdown real, la interfaz lo renderiza (negrita, cursiva, links, párrafos):\n"
    "- **Negrita** (dos asteriscos) para el nombre de cada opción (ej. **Junior Suite**, **Faro de la "
    "Marina**) y SIEMPRE para cifras clave — tiempos, tamaños, capacidades (ej. **20 min.**, **25 m²**) "
    "— nunca en cursiva ni sin formato, con moderación en el resto de la frase.\n"
    "- *Cursiva* (un asterisco) para matices o palabras sueltas que no sean cifras — nunca para "
    "tiempos, tamaños ni capacidades, esas van siempre en negrita.\n"
    "- Cuando menciones 2 o 3 opciones, cada una va en su PROPIO párrafo corto (nombre en negrita, "
    "salto de línea, descripción de una frase, salto de línea, dato clave en negrita) — nunca las "
    "juntes en una sola lista con guiones ni las metas todas en un párrafo corrido.\n"
    "- Links: escribe SIEMPRE como markdown `[texto](url)`, nunca la URL pelada. La url debe ser "
    "EXACTAMENTE un valor que venga en los datos de la herramienta (campo site_url, site_url de "
    "get_contact_info, o whatsapp_link) — nunca inventes ni modifiques una URL. Usa el texto del link "
    "para el nombre de la acción, ej. `[Ver habitaciones →](habitaciones.html#showcase)` o inline como "
    "\"puedes conocer nuestras [habitaciones disponibles](habitaciones.html#showcase)\".\n"
    "- CTA solo cuando aporte valor real (cierre de una respuesta con opciones, o cuando el huésped "
    "quiera reservar/contactar) — no le pongas un link a cada frase ni satures la respuesta de botones.\n\n"
    "Idioma: responde siempre en el mismo idioma en el que te escribe el huésped — si te escribe en "
    "inglés, respóndele en inglés (mismo tono cálido y formal); si te escribe en español, en español.\n\n"
    "Ya lo saludaste y le preguntaste su nombre y si es huésped del hotel o visitante — en cuanto te "
    "los diga, dirígete a él o ella por su nombre el resto de la conversación (con naturalidad, no en "
    "cada frase) y ajusta el enfoque: a un huésped actual háblale de servicios e instalaciones del "
    "hotel primero; a alguien que todavía no se hospeda, ayúdalo a explorar el hotel y a reservar. Si "
    "no contestó nombre o condición, no insistas más de una vez — sigue ayudando con la consulta.\n\n"
    "Cuando una herramienta te devuelva varias opciones (habitaciones, lugares), nunca las listes "
    "todas ni las describas en detalle — elige SOLO 2 o 3 (nunca más de 3, aunque la herramienta te "
    "devuelva 9 o más filas), un bloque corto por opción (ver FORMATO), y después pregunta qué le "
    "interesa más al huésped para profundizar ahí. Nunca respondas solo con preguntas genéricas sin "
    "nombrar ninguna opción concreta.\n\n"
    "Usa SIEMPRE las herramientas disponibles para obtener datos reales antes de responder sobre "
    "habitaciones, políticas, instalaciones, lugares cercanos, restaurantes, cultura u ofertas — "
    "salones y eventos tienen su propia regla especial más abajo, no apliques esta a esos. "
    "Nunca inventes precios, disponibilidad, horarios, capacidades, distancias, medios de transporte, "
    "ni datos históricos, técnicos o de cualquier otro tipo (año de construcción, altura, alcance, "
    "anécdotas) que no estén literalmente en los datos devueltos por las herramientas — si la "
    "herramienta no trae ese detalle, no lo agregues aunque te parezca un dato razonable o conocido. "
    "Cuando los datos incluyan una cifra concreta (m², minutos, capacidad, hora), inclúyela siempre en "
    "tu respuesta, en negrita — no la resumas de forma vaga.\n\n"
    "ÚNICOS canales de contacto reales del hotel — NUNCA menciones un sitio web, teléfono, email o link "
    "distinto a estos, aunque te parezca razonable inventarlo para sonar útil. Si no estás seguro de un "
    "dato de contacto, usa exactamente estos o no lo menciones:\n"
    "- Reservar habitación (online): [Reservar ahora →](https://soldeoro.ihotelier.com/es/book/dates-of-stay)\n"
    "- Reservar habitación (email/teléfono): reservas@soldeoro.pe · +51 (1) 610-7000\n"
    "- Reservar mesa en el restaurante: +51 (1) 610-7000 — para más info del restaurante del hotel "
    "busca en las preguntas frecuentes por el tema restaurante\n"
    "- Eventos / cotizaciones: primero usa la herramienta de consulta de salones para saber si hay "
    "capacidad, luego usa la herramienta de contacto por WhatsApp para eventos — nunca enumeres "
    "salones ni des el link de WhatsApp de memoria\n"
    "- Hablar con el hotel / ayuda personalizada / no puedes resolver algo: usa la herramienta de "
    "contacto por WhatsApp, con el tema de reserva de habitación o general según corresponda\n"
    "- Recepción / lobby — para cualquier otra consulta: +51 (1) 610-7000\n"
    "Trata siempre de resolver toda la consulta del huésped con lo que tienes disponible; si después "
    "de intentarlo no puedes resolver una parte, deriva por WhatsApp en vez de dejarla sin respuesta.\n\n"
    "Instalaciones del hotel (piscina, gimnasio, spa, estacionamiento, Wi-Fi, desayuno, lavandería, "
    "etc.) NO son lo mismo que salones o espacios para eventos, aunque suenen parecido — para "
    "instalaciones usa la herramienta de lugares cercanos con la categoría hotel o la de preguntas "
    "frecuentes, nunca la de salones ni la de contacto por WhatsApp de eventos.\n\n"
    "Eventos — cómo responder, sin excepciones: cuando pregunten específicamente por salones, espacios "
    "para eventos (reuniones, conferencias, matrimonios, celebraciones), o te den una cantidad de "
    "personas para un evento, usa la herramienta de consulta de salones (nunca "
    "la de preguntas frecuentes ni la de habitaciones para esto). Ella te dice si el hotel tiene "
    "capacidad suficiente, pero NUNCA te da nombres de salones, pisos, montajes ni cifras de un salón "
    "individual — esa información no está disponible para ti, ni siquiera si aparece de pasada en el "
    "resultado de otra herramienta (ej. una FAQ que la mencione). Si la herramienta indica que sí hay "
    "capacidad para la cantidad pedida, dilo en una frase breve (ej. \"contamos con espacios que "
    "pueden recibir eventos de hasta X personas\") y ofrece derivar con el equipo comercial para ver "
    "alternativas, montaje y disponibilidad — usa la herramienta de contacto por WhatsApp con el tema "
    "eventos. Si todavía no te dieron la cantidad de personas, pregunta primero qué tipo de evento es "
    "y cuántas personas antes de derivar, así el equipo comercial recibe la consulta con contexto. "
    "Nunca inventes disponibilidad, precio, descuentos ni condiciones comerciales de un evento; si "
    "preguntan por eso, dilo con claridad y deriva.\n\n"
    "Captura de datos: cuando el huésped te dé su nombre, empresa, email, teléfono, o datos de un "
    "evento (tipo, fecha, cantidad de personas, requerimientos), guárdalos con la herramienta de "
    "captura de datos apenas te los diga, sin importar el tema de la conversación — así no se pierden "
    "y no hace falta volver a preguntarlos más adelante en la misma conversación.\n\n"
    "Varias preguntas en un mismo mensaje: si el huésped pregunta por más de un tema a la vez (ej. "
    "habitaciones y restaurante, o eventos y ubicación), puedes usar una herramienta por turno, nunca "
    "dos juntas en la misma respuesta — pide la primera, mira su resultado, y si todavía te falta "
    "información para la otra parte, en tu siguiente turno pide la segunda herramienta ANTES de "
    "responder (no respondas todavía con lo de la primera). Cuando ya tengas lo necesario para las dos "
    "partes, contesta ambas en el mismo mensaje final — nunca cierres solo con la primera parte y una "
    "pregunta de seguimiento, dejando la segunda parte sin responder. Ejemplo: si preguntan \"¿qué "
    "habitación me recomiendas y puedo cenar en el hotel?\", primero pide la herramienta de "
    "habitaciones, después pide la herramienta de preguntas frecuentes con el tema restaurante, y "
    "recién ahí contesta las dos partes juntas.\n\n"
    "Nunca inventes nombres de ejecutivas o ejecutivos comerciales, precios, disponibilidad, "
    "descuentos, cotizaciones ni condiciones comerciales de ningún tipo — si no tienes ese dato de una "
    "herramienta, dilo con honestidad y deriva por WhatsApp.\n\n"
    "Sobre lugares cercanos: la categoría \"hotel\" de get_nearby es solo para instalaciones DENTRO del "
    "hotel (piscina, gimnasio, spa) — úsala para preguntas sobre instalaciones o servicios del hotel. "
    "Para \"qué hacer cerca / afuera del hotel\" en general, considera varias categorías (compras, costa, "
    "paseos) y elige las que mejor calcen con el pedido (pareja o romántico → costa, ej. Malecón o Parque "
    "del Amor; poco tiempo disponible → lo más cercano en minutos; primera vez en Lima → una mezcla "
    "variada). Para miradores, faros, parques o paseos usa siempre get_nearby, nunca get_cultural (esa "
    "es solo para museos y sitios arqueológicos formales).\n\n"
    "Si no tienes el dato, dilo y sugiere contactar al hotel directamente.\n\n"
    "Guía hacia el sitio web: cada fila que te devuelve una herramienta puede traer un campo "
    "\"site_url\" (la ruta real del sitio) y \"site_section\" (su nombre legible). Cuando agregue valor, "
    "cierra con un link markdown usando ese site_url exacto — nunca inventes una sección, botón, link o "
    "página que no venga en los datos. No repitas el link en cada frase de una lista larga: alcanza con "
    "uno al cierre de la respuesta, priorizando siempre llevar al huésped hacia la información o la "
    "acción que ya existe en el sitio antes que explayarte más en el chat."
)


class ConciergeRequest(BaseModel):
    message: str
    session_id: str
    persona: str = _DEFAULT_PERSONA_KEY


class ConciergeResponse(BaseModel):
    message: str
    intent: str
    actions: list[dict]
    images: list[dict] = []


_FALLBACK_MESSAGE = "Dame un momento, tengo un problema técnico para responder eso. Te recomiendo contactar directamente al hotel."
_CONTACT_ACTION = {"type": "CONTACT_HOTEL", "label": "Contactar hotel", "url": "mailto:reservas@soldeoro.pe"}

# Salvaguarda determinística contra alucinación de contacto: en pruebas manuales el modelo
# inventó dominios/teléfonos falsos ("hotelsoldemiraflores.com", "+51 1 242 1234") a pesar de
# que el system prompt ya trae los datos reales — el prompt engineering solo no bastó para
# garantizar esto de forma confiable con un modelo de 8B. Esta función es el guardrail en
# código: nunca se le muestra al huésped un email/teléfono/link de contacto que no sea real.
_ALLOWED_EMAILS = {"reservas@soldeoro.pe", "comercial@soldeoro.pe"}
_ALLOWED_URL_DOMAINS = ("soldeoro.pe", "soldeoro.ihotelier.com", "wa.me")
_ALLOWED_PHONE_DIGITS = {"5116107000", "51924664487"}  # +51 (1) 610-7000 · +51 924 664 487

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_URL_RE = re.compile(r"https?://[^\s\)\]]+")
_PHONE_RE = re.compile(r"\+?51[\s\-]?\(?\d\)?[\s\-\d]{6,}\d")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

_REAL_CONTACT_LINE = (
    "Reservar habitación: https://soldeoro.ihotelier.com/es/book/dates-of-stay · "
    "Contacto: reservas@soldeoro.pe · +51 (1) 610-7000"
)

# Rutas internas reales del sitio — única fuente de verdad para validar links markdown
# `[texto](url)` que el modelo escriba. Cualquier url que no calce exactamente (o no empiece
# con un dominio/permitido de _ALLOWED_URL_DOMAINS o "mailto:") se considera inventada.
_ALLOWED_INTERNAL_PATHS = {
    "habitaciones.html", "habitaciones.html#showcase", "habitaciones.html#reserve",
    "eventos.html", "eventos.html#salones", "eventos.html#capacidad", "eventos.html#reserve",
    "restaurante.html", "restaurante.html#carta", "restaurante.html#reserve",
    "servicios.html", "servicios.html#amenidades",
    "experiencias.html", "experiencias.html#reserve",
    "ofertas.html", "faq.html", "galeria.html", "ubicacion.html", "acerca.html",
    "empresarial.html", "index.html",
}


def _is_allowed_url(url: str) -> bool:
    url = url.strip()
    if url in _ALLOWED_INTERNAL_PATHS:
        return True
    if url.startswith("mailto:"):
        return url[len("mailto:"):] in _ALLOWED_EMAILS
    # Parseado real en vez de "el dominio aparece como substring en algún lado" — un substring
    # check dejaba pasar cosas como "https://evil.com/?x=wa.me" o "javascript:...//soldeoro.pe"
    # solo porque el texto del dominio permitido aparecía en algún punto de la URL.
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    host = (parsed.hostname or "").lower().rstrip(".")
    return any(host == domain or host.endswith(f".{domain}") for domain in _ALLOWED_URL_DOMAINS)


def _sanitize_markdown_links(text: str) -> str:
    # El modelo puede inventar una URL que "suena" real (ej. "habitaciones.html#detalle" cuando
    # el anchor real es "#showcase") — si el link no calza exacto con una ruta real conocida, se
    # deja el texto visible (para no romper la frase) pero se quita el link para no mandar a un
    # huésped a una página/anchor que no existe.
    def _check(m: re.Match) -> str:
        label, url = m.group(1), m.group(2)
        if _is_allowed_url(url):
            return m.group(0)
        return label

    return _MD_LINK_RE.sub(_check, text)


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
        if _is_allowed_url(m.group(0)):
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


def _sanitize_final_text(text: str) -> str:
    return _scrub_fabricated_contact(_sanitize_markdown_links(text))


# Habitaciones y espacios DENTRO del hotel (piscina/gimnasio/spa) son los únicos con fotos que
# vale la pena mostrar en el chat — un par, no una galería completa (pedido explícito: "sin
# bombardeo de imágenes"). Se recolectan candidatas de estos dos tools durante la ronda de
# tool-calling; luego _match_mentioned_images() se queda solo con las que el modelo realmente
# nombró en su respuesta, así las fotos siempre corresponden a lo que se está mostrando.
def _image_candidates_from_tool(tc_name: str, args: dict, tool_result) -> list[dict]:
    if tc_name == "get_rooms" and isinstance(tool_result, list):
        return [{"name": r["name"], "url": r["photo_url"]} for r in tool_result if r.get("name") and r.get("photo_url")]
    if tc_name == "get_nearby" and args.get("cat") == "hotel" and isinstance(tool_result, list):
        return [{"name": r["title"], "url": r["photo_url"]} for r in tool_result if r.get("title") and r.get("photo_url")]
    return []


def _match_mentioned_images(text: str, candidates: list[dict], limit: int = 3) -> list[dict]:
    lower_text = text.lower()
    matched, seen = [], set()
    for c in candidates:
        if c["name"] in seen or c["name"].lower() not in lower_text:
            continue
        seen.add(c["name"])
        matched.append(c)
        if len(matched) >= limit:
            break
    return matched


# El modelo NVIDIA/Llama-3.1-8B-instruct rechaza con un 500 ("This model only supports
# single tool-calls at once") cualquier intento de pedir dos tool-calls en la misma
# respuesta — confirmado en pruebas en vivo al pedirle resolver una pregunta con dos temas a
# la vez. Por eso el soporte de "varias preguntas en un mismo mensaje" es de RONDAS
# sucesivas (una tool por respuesta, hasta _MAX_TOOL_ROUNDS respuestas), nunca de varias
# tools en la misma respuesta.
_MAX_TOOL_ROUNDS = 3


def _resolve_tool_calls(payload: "ConciergeRequest", session: dict) -> tuple[list[dict], dict | None, list[dict]]:
    """Corre hasta _MAX_TOOL_ROUNDS rondas de tool-calling (no es texto visible, no necesita
    streaming) y devuelve los `messages` listos para la síntesis final + el resultado de
    whatsapp handoff si se usó (para saltarse la síntesis por LLM en ese caso — ver
    _build_whatsapp_message) + las fotos candidatas (habitaciones/espacios del hotel) para
    emparejar contra el texto final."""
    messages = [{"role": "system", "content": _build_system_prompt(payload.persona)}, *session["history"]]

    whatsapp_handoff_result = None
    image_candidates: list[dict] = []

    for _round in range(_MAX_TOOL_ROUNDS):
        result = chat(messages=messages, tools=_TOOLS_SPEC)
        if not result["tool_calls"]:
            break
        # Defensivo: si alguna vez llegara más de un tool_call en una misma respuesta (no
        # debería, ver nota arriba), solo se ejecuta el primero para no romper el turno.
        tc = result["tool_calls"][0]
        messages.append({"role": "assistant", "content": result["content"] or "", "tool_calls": [
            {"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": tc["arguments"]}}
        ]})
        try:
            args = json.loads(tc["arguments"]) if tc["arguments"] else {}
        except json.JSONDecodeError:
            # El modelo a veces devuelve JSON de argumentos mal formado (no-determinismo,
            # temperature > 0) — se trata como "sin argumentos" en vez de tumbar el request.
            args = {}
        # Errores de Supabase (timeout, 5xx) se propagan y caen en el except del caller —
        # nunca se inventa el dato faltante, se cae al mensaje de fallback.
        if tc["name"] == "get_whatsapp_handoff":
            # Arma el link de WhatsApp con el historial real de la sesión — no pasa por
            # _TOOL_FUNCS porque necesita la sesión completa (historial + lead), no los
            # argumentos del modelo. Corta las rondas: una vez que se deriva por WhatsApp no
            # tiene sentido seguir pidiendo más tools.
            tool_result = _build_whatsapp_handoff(session, args.get("topic", "general"), payload.session_id)
            whatsapp_handoff_result = tool_result
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": json.dumps(tool_result, ensure_ascii=False)})
            break
        elif tc["name"] == "capture_lead":
            # Igual que el handoff: necesita la sesión completa (para acumular en
            # session["lead"] entre turnos), no pasa por _TOOL_FUNCS.
            tool_result = _capture_lead(session, args)
        else:
            tool_fn = _TOOL_FUNCS.get(tc["name"])
            if tool_fn is None:
                # El modelo puede alucinar un nombre de tool que no declaramos — se devuelve
                # un error legible en el mensaje "tool" para que se recupere en la siguiente
                # llamada en vez de tumbar el request entero.
                tool_result = {"error": f"herramienta desconocida: {tc['name']}"}
            else:
                tool_result = tool_fn(**args)
            image_candidates.extend(_image_candidates_from_tool(tc["name"], args, tool_result))
        messages.append({"role": "tool", "tool_call_id": tc["id"], "content": json.dumps(tool_result, ensure_ascii=False)})

    return messages, whatsapp_handoff_result, image_candidates


@router.post("/api/concierge", response_model=ConciergeResponse)
def concierge(payload: ConciergeRequest) -> ConciergeResponse:
    append_message(payload.session_id, "user", payload.message)
    session = get_session(payload.session_id)

    images: list[dict] = []
    try:
        messages, whatsapp_handoff_result, image_candidates = _resolve_tool_calls(payload, session)

        if whatsapp_handoff_result is not None:
            final_message = _build_whatsapp_message(whatsapp_handoff_result)
            actions = []
        else:
            result = chat(messages=messages)
            final_message = _sanitize_final_text(result["content"]) if result["content"] else _FALLBACK_MESSAGE
            actions = [] if result["content"] else [_CONTACT_ACTION]
            images = _match_mentioned_images(final_message, image_candidates)
    except Exception:
        # Captura fallos de NVIDIA Build (rate limit, timeout, modelo caído) y de Supabase
        # (tool call fallido). Nunca se propaga un 500 crudo al widget ni se inventa contenido.
        logger.exception("Fallo al procesar mensaje del concierge (session_id=%s)", payload.session_id)
        final_message = _FALLBACK_MESSAGE
        actions = [_CONTACT_ACTION]

    append_message(payload.session_id, "assistant", final_message)
    return ConciergeResponse(message=final_message, intent="UNCLASSIFIED", actions=actions, images=images)


# --- Streaming (SSE) --------------------------------------------------------------------
# Streaming real de la respuesta final, no una animación de escritura falsa: se piden los
# tokens al modelo con stream=True y se van soltando al cliente a medida que llegan. La única
# diferencia con una respuesta cruda es que se bufferea por ORACIÓN COMPLETA antes de mandarla
# — los guardrails (link/contacto inventado) necesitan el texto completo de una oración para
# poder validarlo, no tiene sentido (ni es seguro) validar un token suelto a la vez. La ronda
# de tool-calling en sí no se streamea: no es texto visible para el huésped.
# Grupo de captura -> re.split conserva el separador junto con cada oración, para que el
# frontend pueda concatenar los chunks tal cual llegan sin tener que adivinar espacios/saltos.
_SENTENCE_BOUNDARY_RE = re.compile(r"((?<=[.!?])\s+)")


def _split_with_separators(buffer: str) -> tuple[list[str], str]:
    parts = _SENTENCE_BOUNDARY_RE.split(buffer)
    chunks = []
    i = 0
    while i + 1 < len(parts):
        chunks.append(parts[i] + parts[i + 1])
        i += 2
    remainder = parts[i] if i < len(parts) else ""
    return chunks, remainder


def _sse_event(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _stream_concierge_turn(payload: ConciergeRequest):
    append_message(payload.session_id, "user", payload.message)
    session = get_session(payload.session_id)
    full_text = ""
    image_candidates: list[dict] = []

    try:
        messages, whatsapp_handoff_result, image_candidates = _resolve_tool_calls(payload, session)

        if whatsapp_handoff_result is not None:
            # Ya es texto 100% conocido (no se está "generando") — se suelta por oración para
            # mantener el mismo ritmo de lectura progresiva que el resto de las respuestas.
            full_text = _build_whatsapp_message(whatsapp_handoff_result)
            chunks, remainder = _split_with_separators(full_text)
            if remainder:
                chunks.append(remainder)
            for chunk in chunks:
                if chunk.strip():
                    yield _sse_event({"type": "chunk", "text": chunk})
        else:
            buffer = ""
            got_any = False
            for delta in chat_stream(messages):
                got_any = True
                buffer += delta
                complete, buffer = _split_with_separators(buffer)
                for sentence in complete:
                    if not sentence.strip():
                        continue
                    safe = _sanitize_final_text(sentence)
                    full_text += safe
                    yield _sse_event({"type": "chunk", "text": safe})
            if buffer.strip():
                safe = _sanitize_final_text(buffer)
                full_text += safe
                yield _sse_event({"type": "chunk", "text": safe})
            if not got_any or not full_text.strip():
                full_text = _FALLBACK_MESSAGE
                yield _sse_event({"type": "chunk", "text": full_text})
    except Exception:
        logger.exception("Fallo al procesar mensaje del concierge (streaming, session_id=%s)", payload.session_id)
        full_text = _FALLBACK_MESSAGE
        yield _sse_event({"type": "chunk", "text": full_text})

    append_message(payload.session_id, "assistant", full_text)

    images = _match_mentioned_images(full_text, image_candidates)
    if images:
        yield _sse_event({"type": "images", "images": images})
    yield _sse_event({"type": "done"})


@router.post("/api/concierge/stream")
def concierge_stream(payload: ConciergeRequest) -> StreamingResponse:
    return StreamingResponse(_stream_concierge_turn(payload), media_type="text/event-stream")
