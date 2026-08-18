from app.api.concierge import _is_allowed_url, _sanitize_markdown_links, _scrub_fabricated_contact


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
    text = "Escribe a comercial@soldeoro.pe o por WhatsApp a https://wa.me/51924664487"
    assert _scrub_fabricated_contact(text) == text


def test_scrub_allows_real_events_phone():
    text = "Llámanos al +51 924 664 487 para cotizar tu evento."
    assert _scrub_fabricated_contact(text) == text


# Regresión: un check de "el dominio permitido aparece como substring en algún lado" deja
# pasar URLs como "https://evil.com/?x=wa.me" o "https://evilsoldeoro.pe/" — el validador debe
# parsear la URL real y comparar el host exacto, no hacer un substring match del texto crudo.
def test_is_allowed_url_rejects_substring_bypass():
    assert _is_allowed_url("https://evil.com/?x=wa.me") is False
    assert _is_allowed_url("https://evilsoldeoro.pe/") is False
    assert _is_allowed_url("https://attacker.com/habitaciones.html") is False
    assert _is_allowed_url("javascript:alert(1)//soldeoro.pe") is False
    assert _is_allowed_url("mailto:evil@attacker.com") is False


def test_is_allowed_url_accepts_real_channels():
    assert _is_allowed_url("https://wa.me/51924664487?text=hola") is True
    assert _is_allowed_url("https://soldeoro.ihotelier.com/es/book/dates-of-stay") is True
    assert _is_allowed_url("habitaciones.html#showcase") is True
    assert _is_allowed_url("mailto:reservas@soldeoro.pe") is True


def test_sanitize_markdown_links_strips_javascript_scheme():
    text = "Haz clic [aquí](javascript:alert(1)) para más info."
    result = _sanitize_markdown_links(text)
    assert "javascript:" not in result
    assert "aquí" in result


def test_sanitize_markdown_links_keeps_real_internal_link():
    text = "Puedes ver más en [Habitaciones](habitaciones.html#showcase)."
    assert _sanitize_markdown_links(text) == text
