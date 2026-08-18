import time

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def ask(question: str, session_id: str) -> str:
    # Pausa breve entre llamadas: el tier gratuito de NVIDIA Build rate-limita (429) cuando
    # esta suite dispara ~23 requests seguidos sin pausa. No es un fallback silencioso del
    # bug — el 429 real se ve durante el desarrollo; esta pausa evita que la propia suite se
    # auto-sabotee en CI. El endpoint sigue manejando un 429 real con el mensaje de fallback.
    time.sleep(2)
    response = client.post("/api/concierge", json={"message": question, "session_id": session_id})
    assert response.status_code == 200
    return response.json()["message"]


QUESTIONS = [
    # HOTEL
    ("¿Dónde está el hotel?", ["San Martín", "Miraflores"]),
    ("¿Qué habitaciones tienen?", ["Standard", "Suite"]),
    ("¿Qué servicios ofrecen?", ["Wi-Fi", "piscina", "gimnasio", "spa"]),
    ("¿Qué instalaciones tienen?", ["piscina", "gimnasio", "spa"]),
    # EXPERIENCIAS
    ("¿Qué puedo hacer cerca del hotel?", ["Larcomar", "Malecón", "Kennedy"]),
    ("¿Qué puedo hacer caminando desde el hotel?", ["min"]),
    ("Tengo dos horas libres y quiero hacer algo caminando, ¿qué me recomiendas?", ["min"]),
    ("¿Qué puedo hacer con mi pareja cerca del hotel?", ["Parque del Amor", "Malecón", "atardecer"]),
    ("¿Qué puedo hacer en Miraflores?", ["Miraflores"]),
    # CULTURA
    ("¿Qué museos hay cerca?", ["museo", "Museo"]),
    ("¿Qué es Huaca Pucllana?", ["Huaca Pucllana", "preincaic", "pirámide", "Pirámide"]),
    ("¿Cómo voy al Centro Histórico?", ["Centro Histórico", "taxi", "min"]),
    # COMPRAS
    ("¿Dónde puedo comprar souvenirs?", ["Mercado Indio", "artesanía"]),
    ("¿Dónde está Larcomar?", ["Larcomar", "min"]),
    # EVENTOS — Fase 2: ya no deriva a ciegas, primero puede confirmar capacidad agregada
    # (get_salons) y recién después ofrece WhatsApp; por eso el set de keywords es más amplio
    # que antes (cualquiera de las dos etapas del flujo es una respuesta válida).
    ("¿Qué salones tienen?", ["personas", "evento", "WhatsApp", "wa.me", "comercial@soldeoro.pe"]),
    ("Necesito un salón para 80 personas", ["80", "personas", "espacio", "WhatsApp", "wa.me", "comercial@soldeoro.pe"]),
    ("Quiero cotizar un evento", ["comercial@soldeoro.pe", "924 664 487", "WhatsApp", "personas", "tipo de evento"]),
    # RESERVAS
    ("Quiero reservar una habitación", ["ihotelier", "reservar", "Reservar"]),
    ("Quiero contactar al hotel", ["reservas@soldeoro.pe", "610-7000", "WhatsApp"]),
    ("¿Aceptan mascotas?", ["mascota", "perro", "6 kg"]),
]


@pytest.mark.parametrize("question,expected_keywords", QUESTIONS)
def test_question_answered_with_real_data(question, expected_keywords):
    answer = ask(question, session_id=f"20q-{hash(question)}")
    assert any(kw.lower() in answer.lower() for kw in expected_keywords), (
        f"Pregunta: {question!r}\nRespuesta: {answer!r}\nEsperaba alguna de: {expected_keywords}"
    )


# Regresión: en pruebas manuales (Task 12) el modelo inventó un sitio web, teléfono y email
# falsos al cerrar una respuesta sobre habitaciones ("hotelsoldemiraflores.com", "+51 1 222 3333").
# Ninguna de las 20 preguntas de arriba lo detectaba porque solo verifican que el dato correcto
# esté presente, no que no haya datos de contacto fabricados de más.
FABRICATED_CONTACT_PATTERNS = [
    "hotelsoldemiraflores",
    "solesdeoro",
    "222 3333",
    "222-3333",
]


@pytest.mark.parametrize("question", [
    "¿Qué habitaciones tienen?",
    "¿Qué puedo hacer cerca del hotel?",
    "¿Qué servicios ofrecen?",
])
def test_no_fabricated_contact_info(question):
    answer = ask(question, session_id=f"nofab-{hash(question)}")
    lowered = answer.lower()
    for bad in FABRICATED_CONTACT_PATTERNS:
        assert bad not in lowered, f"Pregunta: {question!r}\nRespuesta contiene dato de contacto inventado ({bad!r}): {answer!r}"
    # Si la respuesta menciona un email o teléfono, debe ser uno de los reales.
    if "@" in answer:
        assert "soldeoro.pe" in lowered, f"Email mencionado no es un dominio real del hotel: {answer!r}"
    if "http" in lowered and "soldeoro" not in lowered and "wa.me" not in lowered:
        assert False, f"Link mencionado no es un dominio real del hotel: {answer!r}"


# Regresión Fase 2: get_salons() ahora está reconectada y le da al modelo un resumen de
# capacidad agregado — la regla "nunca menciones nombres de salones" ya no depende solo del
# prompt (la garantía real vive en _get_salons_summary, que nunca incluye nombres), pero esta
# prueba confirma que además no se cuela ningún nombre real por otra vía (ej. una FAQ).
def test_events_answer_never_leaks_real_salon_names():
    from app.tools.supabase import get_salons

    real_names = {s["name"] for s in get_salons()}
    answer = ask("Necesito un salón para 80 personas", session_id="salon-names-leak")
    for name in real_names:
        assert name not in answer, f"La respuesta mencionó el nombre real de un salón ({name!r}): {answer!r}"


# Regresión Fase 2: antes de esta fase, pedirle al modelo resolver dos tools en el mismo
# turno (ej. habitaciones + restaurante) tumbaba el request con un 500 real de la API NVIDIA
# ("This model only supports single tool-calls at once") — ver _resolve_tool_calls, ahora
# hecho de rondas secuenciales (una tool por turno) en vez de varias en la misma respuesta.
# Esta prueba en vivo confirma esa regresión puntual: la pregunta compuesta ya NO tumba el
# turno (no cae al mensaje de fallback) y responde al menos la primera parte. Que el modelo
# de 8B encadene ambas herramientas y cubra las dos partes en la misma respuesta es
# deseable pero no 100% consistente (limitación conocida del tamaño del modelo, no de esta
# arquitectura) — esa cobertura determinística está en
# test_events_and_leads.py::test_resolve_tool_calls_supports_sequential_multi_round, que no
# depende del juicio del LLM.
def test_multi_intent_question_does_not_crash_and_answers_first_part():
    from app.api.concierge import _FALLBACK_MESSAGE

    answer = ask(
        "¿Qué habitación me recomiendas y puedo cenar en el hotel?",
        session_id="multi-intent-rooms-restaurant",
    )
    assert answer != _FALLBACK_MESSAGE, f"El turno cayó al mensaje de fallback (posible 500): {answer!r}"
    lowered = answer.lower()
    assert any(kw in lowered for kw in ["suite", "habitación", "room"]), f"No respondió la parte de habitaciones: {answer!r}"
