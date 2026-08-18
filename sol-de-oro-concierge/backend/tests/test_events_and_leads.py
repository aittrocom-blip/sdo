import urllib.parse

from app.api import concierge as concierge_module
from app.api.concierge import (
    _build_whatsapp_handoff,
    _capture_lead,
    _get_salons_summary,
    _persist_lead,
)
from app.session import get_session


class _FakePayload:
    def __init__(self, session_id, persona="maria_paz"):
        self.session_id = session_id
        self.persona = persona


# get_salons() reconectada al agente — resumen agregado, nunca fila por fila -----------------

def test_salons_summary_never_leaks_row_level_fields():
    summary = _get_salons_summary(guests=80)
    allowed_keys = {
        "has_event_spaces", "requested_guests", "capacity_covers_request",
        "matching_alternatives_count", "max_capacity_available", "site_url", "site_section",
    }
    assert set(summary.keys()) == allowed_keys
    # Ninguna clave de una fila individual (nombre, piso, montaje) puede llegar al LLM.
    assert "name" not in summary
    assert "floor" not in summary
    assert "montajes" not in summary


def test_salons_summary_reports_capacity_for_small_group():
    summary = _get_salons_summary(guests=10)
    assert summary["has_event_spaces"] is True
    assert summary["capacity_covers_request"] is True
    assert summary["matching_alternatives_count"] >= 1


def test_salons_summary_without_guests_only_confirms_spaces_exist():
    summary = _get_salons_summary()
    assert summary["requested_guests"] is None
    assert summary["capacity_covers_request"] is True
    assert summary["has_event_spaces"] is True


def test_salons_summary_coerces_string_guests():
    summary = _get_salons_summary(guests="80")
    assert summary["requested_guests"] == 80


# capture_lead — merge progresivo en sesión, nunca pisa un dato ya conocido con vacío --------

def test_capture_lead_merges_progressively_without_losing_prior_fields():
    session = get_session("test-lead-progressive")
    _capture_lead(session, {"event_type": "Corporativo", "guests": 80})
    result = _capture_lead(session, {"event_date": "20 de septiembre", "guests": None})
    assert session["lead"]["event_type"] == "Corporativo"
    assert session["lead"]["guests"] == 80  # no se pisa con el None del segundo llamado
    assert session["lead"]["event_date"] == "20 de septiembre"
    assert result["known_fields"]["event_type"] == "Corporativo"


def test_capture_lead_coerces_string_guests_to_int():
    session = get_session("test-lead-guests-str")
    _capture_lead(session, {"guests": "80"})
    assert session["lead"]["guests"] == 80


def test_capture_lead_ignores_empty_strings():
    session = get_session("test-lead-empty")
    _capture_lead(session, {"name": "Juan Pérez"})
    _capture_lead(session, {"name": ""})
    assert session["lead"]["name"] == "Juan Pérez"


# Handoff de WhatsApp enriquecido con el lead + persistencia única en Supabase ---------------

def test_whatsapp_handoff_includes_lead_summary_in_message(monkeypatch):
    monkeypatch.setattr("app.api.concierge.tools.insert_lead", lambda payload: {"id": "fake"})
    session = get_session("test-handoff-lead")
    session["history"] = [{"role": "user", "content": "Quiero un evento corporativo para 80 personas"}]
    _capture_lead(session, {
        "name": "Juan Pérez", "company": "ACME", "event_type": "Corporativo",
        "event_date": "20 de septiembre", "guests": 80,
    })
    handoff = _build_whatsapp_handoff(session, "eventos", "test-handoff-lead")
    decoded = urllib.parse.unquote(handoff["whatsapp_link"].split("?text=")[1])
    assert "Juan Pérez" in decoded
    assert "ACME" in decoded
    assert "Corporativo" in decoded
    assert "80" in decoded


def test_whatsapp_handoff_without_lead_falls_back_to_free_text_context():
    session = get_session("test-handoff-no-lead")
    session["history"] = [{"role": "user", "content": "Quiero saber del hotel"}]
    handoff = _build_whatsapp_handoff(session, "general", "test-handoff-no-lead")
    decoded = urllib.parse.unquote(handoff["whatsapp_link"].split("?text=")[1])
    assert "Quiero saber del hotel" in decoded


def test_persist_lead_writes_once_per_session(monkeypatch):
    calls = []
    monkeypatch.setattr("app.api.concierge.tools.insert_lead", lambda payload: calls.append(payload) or {"id": "fake"})
    session = get_session("test-persist-once")
    _capture_lead(session, {"name": "Ana", "guests": 50, "event_type": "Social"})
    _persist_lead(session, "test-persist-once", "eventos")
    _persist_lead(session, "test-persist-once", "eventos")
    assert len(calls) == 1
    assert calls[0]["session_id"] == "test-persist-once"
    assert calls[0]["name"] == "Ana"
    assert calls[0]["status"] == "handoff_requested"
    assert calls[0]["source"] == "ai_concierge"


def test_persist_lead_does_nothing_without_captured_data(monkeypatch):
    calls = []
    monkeypatch.setattr("app.api.concierge.tools.insert_lead", lambda payload: calls.append(payload) or {"id": "fake"})
    session = get_session("test-persist-empty")
    _persist_lead(session, "test-persist-empty", "general")
    assert calls == []


def test_persist_lead_survives_supabase_failure(monkeypatch):
    def _boom(payload):
        raise RuntimeError("supabase caída")

    monkeypatch.setattr("app.api.concierge.tools.insert_lead", _boom)
    session = get_session("test-persist-fail")
    _capture_lead(session, {"name": "Luis"})
    _persist_lead(session, "test-persist-fail", "general")  # no debe lanzar
    assert session["lead"].get("_persisted") is not True


# _resolve_tool_calls — rondas secuenciales de tool-calling ----------------------------------
# Regresión: el modelo NVIDIA/Llama-3.1-8B rechaza con un 500 cualquier respuesta que pida dos
# tool-calls a la vez ("This model only supports single tool-calls at once"), confirmado en
# pruebas en vivo. Estas pruebas mockean `chat` para verificar el mecanismo real de forma
# determinística (sin depender de que el LLM decida encadenar herramientas) — el mismo
# escenario en vivo vive en test_20_questions.py::test_multi_intent_question_does_not_crash_and_answers_first_part.

def test_resolve_tool_calls_supports_sequential_multi_round(monkeypatch):
    calls = {"n": 0}

    def fake_chat(messages, tools=None):
        calls["n"] += 1
        if calls["n"] == 1:
            return {"content": None, "tool_calls": [{"id": "1", "name": "get_rooms", "arguments": "{}"}]}
        if calls["n"] == 2:
            return {"content": None, "tool_calls": [{"id": "2", "name": "get_faq", "arguments": '{"topic": "restaurante"}'}]}
        return {"content": "listo", "tool_calls": []}

    monkeypatch.setattr(concierge_module, "chat", fake_chat)
    session = get_session("seq-round-test")
    messages, whatsapp_result, images = concierge_module._resolve_tool_calls(_FakePayload("seq-round-test"), session)

    assert calls["n"] == 3  # 2 rondas con tool + 1 ronda final sin tool_calls
    assert whatsapp_result is None
    tool_messages = [m for m in messages if m.get("role") == "tool"]
    assert len(tool_messages) == 2  # ambas herramientas se ejecutaron, una por ronda


def test_resolve_tool_calls_stops_at_max_rounds(monkeypatch):
    calls = {"n": 0}

    def fake_chat_always_tool(messages, tools=None):
        calls["n"] += 1
        return {"content": None, "tool_calls": [{"id": str(calls["n"]), "name": "capture_lead", "arguments": '{"name": "Test"}'}]}

    monkeypatch.setattr(concierge_module, "chat", fake_chat_always_tool)
    session = get_session("seq-round-cap")
    concierge_module._resolve_tool_calls(_FakePayload("seq-round-cap"), session)

    assert calls["n"] == concierge_module._MAX_TOOL_ROUNDS


def test_resolve_tool_calls_stops_immediately_on_whatsapp_handoff(monkeypatch):
    calls = {"n": 0}

    def fake_chat(messages, tools=None):
        calls["n"] += 1
        return {"content": None, "tool_calls": [{"id": "1", "name": "get_whatsapp_handoff", "arguments": '{"topic": "eventos"}'}]}

    monkeypatch.setattr(concierge_module, "chat", fake_chat)
    monkeypatch.setattr(concierge_module.tools, "insert_lead", lambda payload: {"id": "fake"})
    session = get_session("seq-round-handoff")
    messages, whatsapp_result, images = concierge_module._resolve_tool_calls(_FakePayload("seq-round-handoff"), session)

    assert calls["n"] == 1  # no sigue pidiendo más rondas una vez que deriva a WhatsApp
    assert whatsapp_result is not None
