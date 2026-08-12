from app.api.concierge import _scrub_fabricated_contact


def test_scrub_removes_fabricated_email_phone_and_url():
    text = (
        "Contacta al +51 1 242 1234 o escribe a reservas@hotelsoldemiraflores.com "
        "o visita http://www.hotelsoldemiraflores.com"
    )
    result = _scrub_fabricated_contact(text)
    assert "hotelsoldemiraflores" not in result
    assert "242 1234" not in result
    assert "reservas@soldeoro.pe" in result
    assert "soldeoro.ihotelier.com" in result


def test_scrub_leaves_real_contact_info_untouched():
    text = "Contacta al +51 (1) 610-7000 o escribe a reservas@soldeoro.pe"
    assert _scrub_fabricated_contact(text) == text


def test_scrub_leaves_text_without_contact_info_untouched():
    text = "Tenemos 9 categorías de habitaciones disponibles."
    assert _scrub_fabricated_contact(text) == text


def test_scrub_allows_real_events_email_and_whatsapp_link():
    text = "Escribe a comercial@soldeoro.pe o por WhatsApp a https://wa.link/dc0dft"
    assert _scrub_fabricated_contact(text) == text
