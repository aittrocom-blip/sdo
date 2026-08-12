from app.session import get_session, append_message, update_context


def test_new_session_starts_empty():
    session = get_session("test-session-1")
    assert session["history"] == []
    assert session["party"] is None
    assert session["time_available_minutes"] is None


def test_append_message_persists_in_session():
    append_message("test-session-2", "user", "Hola")
    append_message("test-session-2", "assistant", "¡Bienvenido!")
    session = get_session("test-session-2")
    assert session["history"] == [
        {"role": "user", "content": "Hola"},
        {"role": "assistant", "content": "¡Bienvenido!"},
    ]


def test_update_context_stores_party_and_time():
    update_context("test-session-3", party="couple", time_available_minutes=60)
    session = get_session("test-session-3")
    assert session["party"] == "couple"
    assert session["time_available_minutes"] == 60
