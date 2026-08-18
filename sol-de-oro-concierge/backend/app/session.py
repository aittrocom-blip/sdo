_SESSIONS: dict[str, dict] = {}


def get_session(session_id: str) -> dict:
    if session_id not in _SESSIONS:
        _SESSIONS[session_id] = {"history": [], "party": None, "time_available_minutes": None, "lead": {}}
    return _SESSIONS[session_id]


def append_message(session_id: str, role: str, content: str) -> None:
    session = get_session(session_id)
    session["history"].append({"role": role, "content": content})


def update_context(session_id: str, **fields) -> None:
    session = get_session(session_id)
    session.update(fields)
