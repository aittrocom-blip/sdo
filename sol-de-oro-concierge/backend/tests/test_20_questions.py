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
    # EVENTOS
    ("¿Qué salones tienen?", ["Ejecutivo", "Empresarial", "Sol de Oro"]),
    ("Necesito un salón para 80 personas", ["Ejecutivo II", "Ejecutivo III", "Empresarial"]),
    ("Quiero cotizar un evento", ["comercial@soldeoro.pe", "988 861 380", "WhatsApp"]),
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
    if "http" in lowered and "soldeoro" not in lowered and "wa.link" not in lowered:
        assert False, f"Link mencionado no es un dominio real del hotel: {answer!r}"
