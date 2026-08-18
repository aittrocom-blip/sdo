# Sol de Oro AI Concierge — Fase 3 (CRM, Restaurante, Producción, Guardrails) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Llevar el AI Concierge de prototipo local a producción: leads de eventos creados de verdad en Zoho CRM, un mini-módulo de reserva de restaurante que notifica por email, el widget abierto proactivamente en Eventos/Restaurante, un guardrail determinista contra contenido prohibido, sesión persistida en Supabase, y el sitio completo + backend desplegados juntos en Vercel.

**Architecture:** Se extienden los módulos existentes de la Fase 1 (`capture_lead`/`_persist_lead` en `concierge.py`, `session.py`, `supabase.py`) en vez de crear un flujo paralelo. Dos clientes HTTP nuevos y aislados (`app/tools/zoho.py`, `app/tools/mail.py`) se enchufan a `_persist_lead` según `lead_type`. La sesión pasa de un dict en memoria a una tabla Supabase (requisito de Vercel: las funciones serverless no comparten memoria entre invocaciones). El sitio estático y el backend se despliegan como un solo proyecto Vercel — el widget llama `/api/concierge` mismo origen, sin CORS cruzado.

**Tech Stack:** Python 3.11+/FastAPI (ya en uso), `httpx` (ya en uso, mismo cliente para Supabase/Zoho/Hostinger Mail), vanilla JS (widget), Vercel (Python serverless + hosting estático), Supabase (PostgREST).

**Spec:** [docs/superpowers/specs/2026-08-18-concierge-fase3-crm-restaurante-produccion-design.md](../specs/2026-08-18-concierge-fase3-crm-restaurante-produccion-design.md)

## Global Constraints

- Zoho CRM solo para `lead_type == "eventos"` — el restaurante nunca toca Zoho (spec, decisión 1).
- Ampliar `capture_lead`/`_persist_lead` existentes, no duplicar un flujo paralelo (spec, decisión 3).
- Deduplicación de leads en Zoho: nativa por email, sin lógica propia (spec, decisión 4).
- El widget se abre proactivo en `eventos.html`/`restaurante.html` la primera vez de la sesión — los `<form>` estáticos existentes se dejan intactos (spec, decisión 5).
- El guardrail de contenido prohibido es determinista (palabra clave, en código), nunca delegado al LLM — corta ANTES de llamar al modelo (spec, decisión 6).
- Sesión persistida en Supabase, no en memoria de proceso — requisito no negociable para Vercel (spec, decisión 7).
- Un solo proyecto Vercel para sitio + backend, mismo origen — sin CORS cruzado, `.htaccess` se reemplaza por `vercel.json` (spec, decisión 8).
- Cualquier fallo de Zoho o de Hostinger Mail se loguea y nunca tumba la respuesta al huésped — mismo patrón que el manejo de errores de Supabase ya existente.
- Si `ZOHO_CLIENT_ID`/`ZOHO_CLIENT_SECRET`/`ZOHO_REFRESH_TOKEN` no están configuradas, el paso de creación de lead en Zoho se omite sin romper nada (confirmado con el usuario — las credenciales llegan más adelante).
- `Fuente_Original` en el lead de Zoho queda pendiente de confirmación de Gerencia (spec, "Puntos abiertos" #1) — el código la manda como campo pero el valor exacto se define antes de activar la escritura real contra el org de producción.
- Proyecto Supabase existente a reutilizar: `fjzshpilzjtfjcouzzzz` (`https://fjzshpilzjtfjcouzzzz.supabase.co`). No crear un proyecto nuevo.

---

## Nota sobre credenciales antes de empezar

1. **Supabase Management API token** (`sbp_...`) — necesario para la Task 1 (crear la tabla `concierge_sessions`). Mismo tipo de token ya usado en las migraciones de Fase 1 (`sol-de-oro-concierge/migrations/run_migration.py`). Pedir confirmación explícita al usuario antes de usarlo.
2. **`VERCEL_TOKEN`** — ya está guardado en `sol-de-oro-concierge/backend/.env` (no committeado). Se usa recién en la Task 13.
3. **Credenciales de Zoho** (`ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`) — el usuario todavía no las tiene (está coordinando con el administrador de la cuenta Zoho). La Task 6 se implementa igual, con `zoho.is_configured()` como guarda — no bloquea el resto del plan. La Task 13 incluye la guía paso a paso para generarlas.
4. **`HOSTINGER_MAIL_TOKEN`** — token de la API de correo de Hostinger (Bearer), con acceso al mailbox `reservas@soldeoro.pe`. Necesario para la Task 7. Igual que con Zoho, `mail.is_configured()` actúa de guarda si todavía no está.

---

### Task 1: Migración Supabase — tabla `concierge_sessions`

**Files:**
- Create: `sol-de-oro-concierge/migrations/003_create_concierge_sessions.sql`

**Interfaces:**
- Produces: tabla `concierge_sessions` (columnas `session_id` PK, `persona`, `history` jsonb, `lead` jsonb, `party`, `time_available_minutes`, `page_context`, `created_at`) — consumida por Task 2.

- [ ] **Step 1: Crear el archivo de migración**

```sql
-- 5. CONCIERGE_SESSIONS -----------------------------------------------------
-- Reemplaza el dict en memoria de app/session.py (Fase 1) — necesario para correr en
-- funciones serverless (Vercel), que no comparten memoria entre invocaciones. El backend
-- opera con SUPABASE_ANON_KEY (rol anon), igual que el resto de este backend — a
-- diferencia de concierge_leads, acá SÍ hace falta que el rol anon pueda SELECT/UPDATE,
-- no solo INSERT, porque el propio backend necesita leer y actualizar la sesión en cada
-- turno. Esto es seguro porque la anon key nunca se expone al navegador: solo la usa
-- este backend server-side (mismo modelo de confianza que ya aplica a rooms/salons/faq).
CREATE TABLE concierge_sessions (
  session_id text primary key,
  persona text,
  history jsonb not null default '[]'::jsonb,
  lead jsonb not null default '{}'::jsonb,
  party text,
  time_available_minutes int,
  page_context text,
  created_at timestamptz not null default now()
);

ALTER TABLE concierge_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_read_sessions"   ON concierge_sessions FOR SELECT USING (true);
CREATE POLICY "service_insert_sessions" ON concierge_sessions FOR INSERT WITH CHECK (true);
CREATE POLICY "service_update_sessions" ON concierge_sessions FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "admin_all_sessions"      ON concierge_sessions FOR ALL    USING (auth.role() = 'authenticated');
```

- [ ] **Step 2: Ejecutar la migración**

Pedir al usuario el Supabase Management API token, luego correr desde `sol-de-oro-concierge/migrations/`:

```bash
python run_migration.py <management_token> 003_create_concierge_sessions.sql
```

Expected: `200` impreso en la salida (mismo patrón que `run_migration.py` ya usa para las migraciones de Fase 1).

- [ ] **Step 3: Verificar que la tabla existe**

```bash
python -c "import requests; r = requests.get('https://fjzshpilzjtfjcouzzzz.supabase.co/rest/v1/concierge_sessions?select=session_id&limit=1', headers={'apikey': 'sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY'}); print(r.status_code, r.text)"
```

Expected: `200 []` (tabla vacía, sin error de "relation does not exist").

- [ ] **Step 4: Commit**

```bash
git add sol-de-oro-concierge/migrations/003_create_concierge_sessions.sql
git commit -m "feat(concierge): add concierge_sessions table migration"
```

---

### Task 2: `app/tools/supabase.py` — helpers de sesión

**Files:**
- Modify: `sol-de-oro-concierge/backend/app/tools/supabase.py`
- Test: `sol-de-oro-concierge/backend/tests/test_tools_supabase_sessions.py`

**Interfaces:**
- Consumes: `_get(path, params)`, `_post(path, body)` ya existentes en el mismo archivo.
- Produces: `get_session_row(session_id: str) -> dict | None`, `upsert_session_row(session_id: str, fields: dict) -> dict` — consumidos por Task 3.

- [ ] **Step 1: Escribir el test que falla**

`tests/test_tools_supabase_sessions.py`:

```python
from app.tools.supabase import get_session_row, upsert_session_row


def test_get_session_row_returns_none_when_missing():
    assert get_session_row("does-not-exist-yet") is None


def test_upsert_then_get_session_row_roundtrips():
    upsert_session_row("test-supabase-session-1", {
        "persona": "carlos",
        "history": [{"role": "user", "content": "Hola"}],
        "lead": {"name": "Ana"},
    })
    row = get_session_row("test-supabase-session-1")
    assert row["persona"] == "carlos"
    assert row["history"] == [{"role": "user", "content": "Hola"}]
    assert row["lead"] == {"name": "Ana"}


def test_upsert_session_row_overwrites_on_conflict():
    upsert_session_row("test-supabase-session-2", {"persona": "claudia", "history": []})
    upsert_session_row("test-supabase-session-2", {"persona": "claudia", "history": [{"role": "user", "content": "hey"}]})
    row = get_session_row("test-supabase-session-2")
    assert row["history"] == [{"role": "user", "content": "hey"}]
```

- [ ] **Step 2: Correr los tests, verificar que fallan**

Run: `pytest tests/test_tools_supabase_sessions.py -v`
Expected: FAIL — `ImportError: cannot import name 'get_session_row'`

- [ ] **Step 3: Implementar los helpers**

Agregar al final de `app/tools/supabase.py`:

```python
def _upsert(path: str, body: dict, on_conflict: str) -> dict:
    headers = {**_HEADERS, "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates,return=representation"}
    resp = httpx.post(f"{settings.supabase_url}/rest/v1/{path}?on_conflict={on_conflict}", headers=headers, json=body, timeout=15)
    resp.raise_for_status()
    rows = resp.json()
    return rows[0] if rows else {}


def get_session_row(session_id: str) -> dict | None:
    rows = _get("concierge_sessions", {"select": "*", "session_id": f"eq.{session_id}"})
    return rows[0] if rows else None


def upsert_session_row(session_id: str, fields: dict) -> dict:
    return _upsert("concierge_sessions", {"session_id": session_id, **fields}, on_conflict="session_id")
```

- [ ] **Step 4: Correr los tests, verificar que pasan**

Run: `pytest tests/test_tools_supabase_sessions.py -v`
Expected: PASS (requiere que la Task 1 ya se haya ejecutado contra Supabase)

- [ ] **Step 5: Commit**

```bash
git add sol-de-oro-concierge/backend/app/tools/supabase.py sol-de-oro-concierge/backend/tests/test_tools_supabase_sessions.py
git commit -m "feat(concierge): add Supabase-backed session row helpers"
```

---

### Task 3: `app/session.py` — sesión persistida en Supabase

**Files:**
- Modify: `sol-de-oro-concierge/backend/app/session.py` (reescritura completa, mismo archivo)
- Modify: `sol-de-oro-concierge/backend/tests/test_session.py` (reescritura completa — la API cambia de firma)

**Interfaces:**
- Consumes: `tools.get_session_row(session_id)`, `tools.upsert_session_row(session_id, fields)` (Task 2).
- Produces: `get_session(session_id: str) -> dict`, `append_message(session: dict, role: str, content: str) -> None`, `update_context(session: dict, **fields) -> None`, `save_session(session_id: str, session: dict) -> None`. **Cambio de firma importante respecto a Fase 1**: `append_message` y `update_context` ahora reciben el dict `session` (no el `session_id` string) y solo mutan en memoria — no hacen I/O. El I/O se hace una sola vez por request, con `save_session`, al final. Task 4 consume estas cuatro funciones.

- [ ] **Step 1: Escribir los tests que fallan (reemplazan a los de Fase 1)**

`tests/test_session.py`:

```python
from app.session import get_session, append_message, update_context, save_session


def test_new_session_starts_empty():
    session = get_session("test-session-new-1")
    assert session["history"] == []
    assert session["party"] is None
    assert session["time_available_minutes"] is None
    assert session["lead"] == {}
    assert session["page_context"] is None


def test_append_message_mutates_in_memory_only():
    session = get_session("test-session-new-2")
    append_message(session, "user", "Hola")
    append_message(session, "assistant", "¡Bienvenido!")
    assert session["history"] == [
        {"role": "user", "content": "Hola"},
        {"role": "assistant", "content": "¡Bienvenido!"},
    ]


def test_update_context_stores_party_and_time():
    session = get_session("test-session-new-3")
    update_context(session, party="couple", time_available_minutes=60)
    assert session["party"] == "couple"
    assert session["time_available_minutes"] == 60


def test_save_session_then_get_session_roundtrips():
    session = get_session("test-session-new-4")
    append_message(session, "user", "Hola")
    session["lead"]["name"] = "Ana"
    session["page_context"] = "eventos"
    save_session("test-session-new-4", session)

    reloaded = get_session("test-session-new-4")
    assert reloaded["history"] == [{"role": "user", "content": "Hola"}]
    assert reloaded["lead"] == {"name": "Ana"}
    assert reloaded["page_context"] == "eventos"
```

- [ ] **Step 2: Correr los tests, verificar que fallan**

Run: `pytest tests/test_session.py -v`
Expected: FAIL — `TypeError` (firma vieja de `append_message`/`update_context` no acepta un dict como primer argumento, y `save_session` no existe)

- [ ] **Step 3: Reescribir `app/session.py`**

```python
from app.tools import supabase as tools


def _empty_session() -> dict:
    return {
        "history": [],
        "party": None,
        "time_available_minutes": None,
        "lead": {},
        "persona": None,
        "page_context": None,
    }


def get_session(session_id: str) -> dict:
    row = tools.get_session_row(session_id)
    if row is None:
        return _empty_session()
    return {
        "history": row.get("history") or [],
        "party": row.get("party"),
        "time_available_minutes": row.get("time_available_minutes"),
        "lead": row.get("lead") or {},
        "persona": row.get("persona"),
        "page_context": row.get("page_context"),
    }


def append_message(session: dict, role: str, content: str) -> None:
    session["history"].append({"role": role, "content": content})


def update_context(session: dict, **fields) -> None:
    session.update(fields)


def save_session(session_id: str, session: dict) -> None:
    tools.upsert_session_row(session_id, {
        "history": session["history"],
        "party": session.get("party"),
        "time_available_minutes": session.get("time_available_minutes"),
        "lead": session.get("lead") or {},
        "persona": session.get("persona"),
        "page_context": session.get("page_context"),
    })
```

- [ ] **Step 4: Correr los tests, verificar que pasan**

Run: `pytest tests/test_session.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add sol-de-oro-concierge/backend/app/session.py sol-de-oro-concierge/backend/tests/test_session.py
git commit -m "feat(concierge): persist session in Supabase instead of process memory"
```

---

### Task 4: `app/api/concierge.py` — enchufar la sesión nueva + `page_context`

**Files:**
- Modify: `sol-de-oro-concierge/backend/app/api/concierge.py`
- Modify: `sol-de-oro-concierge/backend/tests/test_api_concierge.py`
- Modify: `sol-de-oro-concierge/backend/tests/test_events_and_leads.py` (los `_FakePayload` usados ahí necesitan el atributo `page_context`)

**Interfaces:**
- Consumes: `get_session`, `append_message`, `save_session` de `app.session` (Task 3).
- Produces: `ConciergeRequest.page_context: str | None` — no consumido por otras tasks de este plan, pero es el campo que `concierge.js` (Task 10) empieza a mandar.

- [ ] **Step 1: Escribir el test que falla**

Agregar a `tests/test_api_concierge.py`:

```python
def test_concierge_persists_history_across_requests():
    r1 = client.post("/api/concierge", json={"message": "Hola, soy Juan", "session_id": "test-persist-e2e-1"})
    assert r1.status_code == 200
    r2 = client.post("/api/concierge", json={"message": "¿Cómo me llamo?", "session_id": "test-persist-e2e-1"})
    assert r2.status_code == 200
    # No se verifica el contenido de la respuesta (depende del LLM) — se verifica que la
    # sesión sobrevivió entre dos requests HTTP separados, que es lo que antes garantizaba
    # el dict en memoria y ahora debe garantizar Supabase.
    from app.session import get_session
    session = get_session("test-persist-e2e-1")
    assert len(session["history"]) == 4  # 2 user + 2 assistant


def test_concierge_stores_page_context_on_session():
    client.post("/api/concierge", json={
        "message": "Quiero cotizar un evento",
        "session_id": "test-page-context-1",
        "page_context": "eventos",
    })
    from app.session import get_session
    session = get_session("test-page-context-1")
    assert session["page_context"] == "eventos"
```

- [ ] **Step 2: Correr los tests, verificar que fallan**

Run: `pytest tests/test_api_concierge.py -v`
Expected: FAIL — `page_context` no es un campo aceptado por `ConciergeRequest` (Pydantic lo ignora o el test de `get_session` no encuentra el dato)

- [ ] **Step 3: Modificar `ConciergeRequest`**

En `app/api/concierge.py`, reemplazar:

```python
class ConciergeRequest(BaseModel):
    message: str
    session_id: str
    persona: str = _DEFAULT_PERSONA_KEY
```

por:

```python
class ConciergeRequest(BaseModel):
    message: str
    session_id: str
    persona: str = _DEFAULT_PERSONA_KEY
    page_context: str | None = None
```

- [ ] **Step 4: Actualizar el import de `app.session`**

Reemplazar:

```python
from app.session import append_message, get_session
```

por:

```python
from app.session import append_message, get_session, save_session
```

- [ ] **Step 5: Agregar el hint de `page_context` al system prompt**

Reemplazar:

```python
def _build_system_prompt(persona_key: str) -> str:
    persona = _PERSONAS.get(persona_key, _PERSONAS[_DEFAULT_PERSONA_KEY])
    return _SYSTEM_PROMPT_TEMPLATE.replace("{{NAME}}", persona["name"]).replace("{{FLAVOR}}", persona["flavor"])
```

por:

```python
# Cuando el widget se abre proactivo en eventos.html/restaurante.html (ver concierge.js),
# manda page_context en cada request — esto prioriza las preguntas calificadoras correctas
# desde el primer turno, en vez de depender de que el modelo lo infiera solo.
_PAGE_CONTEXT_HINTS = {
    "eventos": (
        "El huésped te está escribiendo desde la página de Eventos del sitio — asume que "
        "probablemente quiere cotizar o consultar por un evento. Si todavía no te dijo qué "
        "necesita, pregúntale primero si es un evento social o corporativo, la fecha, y la "
        "cantidad de personas, y guarda cada dato con la herramienta de captura apenas te lo diga."
    ),
    "restaurante": (
        "El huésped te está escribiendo desde la página de Restaurante del sitio — asume que "
        "probablemente quiere reservar una mesa o el desayuno buffet. Si todavía no te lo dijo, "
        "pregúntale primero si es mesa o desayuno buffet, la fecha, la hora y la cantidad de "
        "personas, y guarda cada dato con la herramienta de captura apenas te lo diga. Aclara "
        "siempre que la reserva queda sujeta a confirmación del hotel — hay disponibilidad en "
        "general, pero no es automática."
    ),
}


def _build_system_prompt(persona_key: str, page_context: str | None = None) -> str:
    persona = _PERSONAS.get(persona_key, _PERSONAS[_DEFAULT_PERSONA_KEY])
    prompt = _SYSTEM_PROMPT_TEMPLATE.replace("{{NAME}}", persona["name"]).replace("{{FLAVOR}}", persona["flavor"])
    hint = _PAGE_CONTEXT_HINTS.get(page_context)
    if hint:
        prompt += "\n\n" + hint
    return prompt
```

- [ ] **Step 6: Pasar `page_context` en `_resolve_tool_calls`**

Reemplazar la primera línea de `_resolve_tool_calls`:

```python
    messages = [{"role": "system", "content": _build_system_prompt(payload.persona)}, *session["history"]]
```

por:

```python
    messages = [{"role": "system", "content": _build_system_prompt(payload.persona, session.get("page_context"))}, *session["history"]]
```

- [ ] **Step 7: Reescribir el endpoint `/api/concierge`**

Reemplazar:

```python
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
        logger.exception("Fallo al procesar mensaje del concierge (session_id=%s)", payload.session_id)
        final_message = _FALLBACK_MESSAGE
        actions = [_CONTACT_ACTION]

    append_message(payload.session_id, "assistant", final_message)
    return ConciergeResponse(message=final_message, intent="UNCLASSIFIED", actions=actions, images=images)
```

por:

```python
@router.post("/api/concierge", response_model=ConciergeResponse)
def concierge(payload: ConciergeRequest) -> ConciergeResponse:
    session = get_session(payload.session_id)
    if payload.page_context:
        session["page_context"] = payload.page_context
    append_message(session, "user", payload.message)

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
        logger.exception("Fallo al procesar mensaje del concierge (session_id=%s)", payload.session_id)
        final_message = _FALLBACK_MESSAGE
        actions = [_CONTACT_ACTION]

    append_message(session, "assistant", final_message)
    save_session(payload.session_id, session)
    return ConciergeResponse(message=final_message, intent="UNCLASSIFIED", actions=actions, images=images)
```

(Nota: el guardrail de contenido prohibido `_is_prohibited_content`/`_PROHIBITED_MESSAGE` todavía no existe — se agrega recién en la Task 9, que hace su propia modificación incremental sobre este mismo endpoint. No referenciarlo acá todavía, o los tests de esta task fallarían con `NameError`.)

- [ ] **Step 8: Reescribir `_stream_concierge_turn` y `concierge_stream`**

Reemplazar:

```python
def _stream_concierge_turn(payload: ConciergeRequest):
    append_message(payload.session_id, "user", payload.message)
    session = get_session(payload.session_id)
    full_text = ""
    image_candidates: list[dict] = []
```

por:

```python
def _stream_concierge_turn(payload: ConciergeRequest, session: dict):
    if payload.page_context:
        session["page_context"] = payload.page_context
    append_message(session, "user", payload.message)
    full_text = ""
    image_candidates: list[dict] = []
```

y reemplazar el final de la función:

```python
    append_message(payload.session_id, "assistant", full_text)

    images = _match_mentioned_images(full_text, image_candidates)
    if images:
        yield _sse_event({"type": "images", "images": images})
    yield _sse_event({"type": "done"})


@router.post("/api/concierge/stream")
def concierge_stream(payload: ConciergeRequest) -> StreamingResponse:
    return StreamingResponse(_stream_concierge_turn(payload), media_type="text/event-stream")
```

por:

```python
    append_message(session, "assistant", full_text)
    save_session(payload.session_id, session)

    images = _match_mentioned_images(full_text, image_candidates)
    if images:
        yield _sse_event({"type": "images", "images": images})
    yield _sse_event({"type": "done"})


@router.post("/api/concierge/stream")
def concierge_stream(payload: ConciergeRequest) -> StreamingResponse:
    session = get_session(payload.session_id)
    return StreamingResponse(_stream_concierge_turn(payload, session), media_type="text/event-stream")
```

- [ ] **Step 9: Actualizar `_FakePayload` en `test_events_and_leads.py`**

En `tests/test_events_and_leads.py`, reemplazar:

```python
class _FakePayload:
    def __init__(self, session_id, persona="maria_paz"):
        self.session_id = session_id
        self.persona = persona
```

por:

```python
class _FakePayload:
    def __init__(self, session_id, persona="maria_paz", page_context=None):
        self.session_id = session_id
        self.persona = persona
        self.page_context = page_context
```

- [ ] **Step 10: Correr toda la suite, verificar que pasa**

Run: `pytest tests/ -v`
Expected: PASS para `test_api_concierge.py` y `test_events_and_leads.py` — los tests de la Task 9 (`_is_prohibited_content`) todavía no existen, se agregan en esa task.

- [ ] **Step 11: Commit**

```bash
git add sol-de-oro-concierge/backend/app/api/concierge.py sol-de-oro-concierge/backend/tests/test_api_concierge.py sol-de-oro-concierge/backend/tests/test_events_and_leads.py
git commit -m "feat(concierge): wire Supabase-backed session and page_context into endpoints"
```

---

### Task 5: `capture_lead` — agregar el campo `time`

**Files:**
- Modify: `sol-de-oro-concierge/backend/app/api/concierge.py`
- Modify: `sol-de-oro-concierge/backend/tests/test_events_and_leads.py`

**Interfaces:**
- Produces: `_LEAD_FIELDS` incluye `"time"` — consumido por Task 8 (`_persist_lead` → `mail.send_reservation_notification`).

- [ ] **Step 1: Escribir el test que falla**

Agregar a `tests/test_events_and_leads.py`:

```python
def test_capture_lead_accepts_time_field():
    session = get_session("test-lead-time")
    _capture_lead(session, {"event_type": "Mesa", "event_date": "20 de septiembre", "time": "8:30pm", "guests": 4})
    assert session["lead"]["time"] == "8:30pm"
```

- [ ] **Step 2: Correr el test, verificar que falla**

Run: `pytest tests/test_events_and_leads.py::test_capture_lead_accepts_time_field -v`
Expected: FAIL — `KeyError: 'time'` (el campo se descarta silenciosamente porque no está en `_LEAD_FIELDS`)

- [ ] **Step 3: Agregar `time` a `_LEAD_FIELDS`, `_LEAD_LABELS` y al tool spec**

Reemplazar:

```python
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
```

por:

```python
_LEAD_FIELDS = ("name", "email", "phone", "company", "lead_type", "event_type", "event_date", "time", "guests", "requirements")
_LEAD_LABELS = {
    "name": "Nombre",
    "company": "Empresa",
    "event_type": "Tipo",
    "event_date": "Fecha",
    "time": "Hora",
    "guests": "Asistentes",
    "requirements": "Requerimientos",
    "email": "Email",
    "phone": "Teléfono",
}
```

En `_TOOLS_SPEC`, dentro de la definición de `capture_lead`, agregar la propiedad `time` (después de `event_date`):

```python
        "event_date": {"type": "string", "description": "Fecha del evento tal como la dio el huésped, ej. '20 de septiembre'"},
        "time": {"type": "string", "description": "Hora tal como la dio el huésped, ej. '8:30pm' — se usa para reservas de restaurante (mesa o desayuno buffet)"},
        "guests": {"type": "integer"},
```

- [ ] **Step 4: Correr el test, verificar que pasa**

Run: `pytest tests/test_events_and_leads.py::test_capture_lead_accepts_time_field -v`
Expected: PASS

- [ ] **Step 5: Correr toda la suite de este archivo**

Run: `pytest tests/test_events_and_leads.py -v`
Expected: PASS (todos, incluidos los tests de Fase 1 que no deberían romperse)

- [ ] **Step 6: Commit**

```bash
git add sol-de-oro-concierge/backend/app/api/concierge.py sol-de-oro-concierge/backend/tests/test_events_and_leads.py
git commit -m "feat(concierge): add time field to capture_lead for restaurant reservations"
```

---

### Task 6: `app/tools/zoho.py` — cliente OAuth + creación de Lead

**Files:**
- Create: `sol-de-oro-concierge/backend/app/tools/zoho.py`
- Modify: `sol-de-oro-concierge/backend/app/config/settings.py`
- Modify: `sol-de-oro-concierge/backend/.env.example`
- Test: `sol-de-oro-concierge/backend/tests/test_tools_zoho.py`

**Interfaces:**
- Consumes: `settings.zoho_client_id`, `settings.zoho_client_secret`, `settings.zoho_refresh_token` (nuevos, este task).
- Produces: `zoho.is_configured() -> bool`, `zoho.create_lead_from_capture(lead: dict) -> None` — consumido por Task 8.

- [ ] **Step 1: Agregar los campos nuevos a `Settings`**

En `app/config/settings.py`, reemplazar:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str
    supabase_anon_key: str
    nvidia_api_key: str
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"


settings = Settings()
```

por:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str
    supabase_anon_key: str
    nvidia_api_key: str
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    zoho_client_id: str | None = None
    zoho_client_secret: str | None = None
    zoho_refresh_token: str | None = None
    hostinger_mail_token: str | None = None


settings = Settings()
```

- [ ] **Step 2: Agregar los campos nuevos a `.env.example`**

Agregar al final de `.env.example`:

```text
ZOHO_CLIENT_ID=
ZOHO_CLIENT_SECRET=
ZOHO_REFRESH_TOKEN=
HOSTINGER_MAIL_TOKEN=
```

- [ ] **Step 3: Escribir el test que falla**

`tests/test_tools_zoho.py`:

```python
import app.tools.zoho as zoho_module
from app.tools.zoho import is_configured, create_lead_from_capture


class _FakeResponse:
    def __init__(self, json_body, status_code=200):
        self._json = json_body
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._json


def test_is_configured_false_without_credentials(monkeypatch):
    monkeypatch.setattr(zoho_module.settings, "zoho_client_id", None)
    monkeypatch.setattr(zoho_module.settings, "zoho_client_secret", None)
    monkeypatch.setattr(zoho_module.settings, "zoho_refresh_token", None)
    assert is_configured() is False


def test_is_configured_true_with_all_credentials(monkeypatch):
    monkeypatch.setattr(zoho_module.settings, "zoho_client_id", "id")
    monkeypatch.setattr(zoho_module.settings, "zoho_client_secret", "secret")
    monkeypatch.setattr(zoho_module.settings, "zoho_refresh_token", "refresh")
    assert is_configured() is True


def test_create_lead_from_capture_maps_social_event_fields(monkeypatch):
    monkeypatch.setattr(zoho_module.settings, "zoho_client_id", "id")
    monkeypatch.setattr(zoho_module.settings, "zoho_client_secret", "secret")
    monkeypatch.setattr(zoho_module.settings, "zoho_refresh_token", "refresh")
    zoho_module._cached_token.clear()

    calls = []

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        if url == zoho_module._TOKEN_URL:
            return _FakeResponse({"access_token": "tok-123", "expires_in": 3600})
        return _FakeResponse({"data": [{"code": "SUCCESS"}]})

    monkeypatch.setattr(zoho_module.httpx, "post", fake_post)

    create_lead_from_capture({
        "name": "Ana Torres", "email": "ana@example.com", "phone": "+51999999999",
        "event_type": "Social", "event_date": "20 de septiembre", "guests": 80,
        "requirements": "Salón con vista",
    })

    assert len(calls) == 2
    token_call, lead_call = calls
    assert token_call[0] == zoho_module._TOKEN_URL
    assert lead_call[0] == zoho_module._LEADS_URL
    sent_fields = lead_call[1]["json"]["data"][0]
    assert sent_fields["Last_Name"] == "Torres"
    assert sent_fields["First_Name"] == "Ana"
    assert sent_fields["Email"] == "ana@example.com"
    assert sent_fields["Tipo_de_consulta"] == "Social"
    assert sent_fields["Fecha_evento_social"] == "20 de septiembre"
    assert sent_fields["Invitados_evento_social"] == 80
    assert lead_call[1]["json"]["trigger"] == ["workflow"]
    assert lead_call[1]["headers"]["Authorization"] == "Zoho-oauthtoken tok-123"


def test_create_lead_from_capture_maps_corporate_event_fields(monkeypatch):
    monkeypatch.setattr(zoho_module.settings, "zoho_client_id", "id")
    monkeypatch.setattr(zoho_module.settings, "zoho_client_secret", "secret")
    monkeypatch.setattr(zoho_module.settings, "zoho_refresh_token", "refresh")
    zoho_module._cached_token.clear()

    calls = []

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        if url == zoho_module._TOKEN_URL:
            return _FakeResponse({"access_token": "tok-123", "expires_in": 3600})
        return _FakeResponse({"data": [{"code": "SUCCESS"}]})

    monkeypatch.setattr(zoho_module.httpx, "post", fake_post)

    create_lead_from_capture({
        "name": "Luis Pérez", "event_type": "Corporativo", "event_date": "5 de octubre", "guests": 40,
    })

    lead_call = calls[1]
    sent_fields = lead_call[1]["json"]["data"][0]
    assert sent_fields["Tipo_de_consulta"] == "Corporativo"
    assert sent_fields["Fecha_evento_corporativo"] == "5 de octubre"
    assert sent_fields["Asistentes_evento_corp"] == 40


def test_create_lead_from_capture_reuses_cached_token(monkeypatch):
    monkeypatch.setattr(zoho_module.settings, "zoho_client_id", "id")
    monkeypatch.setattr(zoho_module.settings, "zoho_client_secret", "secret")
    monkeypatch.setattr(zoho_module.settings, "zoho_refresh_token", "refresh")
    zoho_module._cached_token.clear()

    calls = []

    def fake_post(url, **kwargs):
        calls.append(url)
        if url == zoho_module._TOKEN_URL:
            return _FakeResponse({"access_token": "tok-123", "expires_in": 3600})
        return _FakeResponse({"data": [{"code": "SUCCESS"}]})

    monkeypatch.setattr(zoho_module.httpx, "post", fake_post)

    create_lead_from_capture({"name": "Ana Torres", "event_type": "Social"})
    create_lead_from_capture({"name": "Ana Torres", "event_type": "Social"})

    token_calls = [c for c in calls if c == zoho_module._TOKEN_URL]
    assert len(token_calls) == 1  # el segundo create_lead reusa el token cacheado
```

- [ ] **Step 4: Correr los tests, verificar que fallan**

Run: `pytest tests/test_tools_zoho.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.tools.zoho'`

- [ ] **Step 5: Implementar `app/tools/zoho.py`**

```python
import time

import httpx

from app.config.settings import settings

# Self Client OAuth (Zoho): refresh_token de larga duración → access_token de 1h. Se cachea
# en memoria del proceso — en Vercel esto significa un refresh extra por cold start, que es
# un costo aceptable (no afecta corrección, solo agrega una llamada ocasional a Zoho).
_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"
_LEADS_URL = "https://www.zohoapis.com/crm/v2/Leads"

_cached_token: dict = {}


def is_configured() -> bool:
    return bool(settings.zoho_client_id and settings.zoho_client_secret and settings.zoho_refresh_token)


def _get_access_token() -> str:
    now = time.time()
    if _cached_token.get("access_token") and _cached_token.get("expires_at", 0) > now + 60:
        return _cached_token["access_token"]
    resp = httpx.post(_TOKEN_URL, params={
        "refresh_token": settings.zoho_refresh_token,
        "client_id": settings.zoho_client_id,
        "client_secret": settings.zoho_client_secret,
        "grant_type": "refresh_token",
    }, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    _cached_token["access_token"] = data["access_token"]
    _cached_token["expires_at"] = now + data.get("expires_in", 3600)
    return _cached_token["access_token"]


# Mapea el lead acumulado por capture_lead (ver concierge.py) a los campos reales del
# módulo Posibles clientes (Leads) del CRM Sol de Oro — misma convención de nombres de
# campo que eventos.html ya usa (Tipo_evento_social/Tipo_evento_corp), alineada con el
# requerimiento Etapa 1 del CRM (skill zoho-crm-expert, sol-de-oro-conventions.md).
def _map_lead_fields(lead: dict) -> dict:
    name_parts = (lead.get("name") or "").strip().split(" ", 1)
    first_name = name_parts[0] if len(name_parts) > 1 else ""
    last_name = name_parts[1] if len(name_parts) > 1 else (name_parts[0] if name_parts and name_parts[0] else "Sin nombre")

    is_social = lead.get("event_type", "").strip().lower() == "social"
    fields = {
        "Last_Name": last_name,
        "Tipo_de_consulta": lead.get("event_type") or "Social",
    }
    if first_name:
        fields["First_Name"] = first_name
    if lead.get("email"):
        fields["Email"] = lead["email"]
    if lead.get("phone"):
        fields["Phone"] = lead["phone"]
    if lead.get("event_date"):
        fields["Fecha_evento_social" if is_social else "Fecha_evento_corporativo"] = lead["event_date"]
    if lead.get("guests"):
        fields["Invitados_evento_social" if is_social else "Asistentes_evento_corp"] = lead["guests"]
    if lead.get("requirements"):
        fields["Servicios_evento_social" if is_social else "Servicios_evento_corp"] = lead["requirements"]
    return fields


def create_lead_from_capture(lead: dict) -> None:
    token = _get_access_token()
    headers = {"Authorization": f"Zoho-oauthtoken {token}", "Content-Type": "application/json"}
    body = {"data": [_map_lead_fields(lead)], "trigger": ["workflow"]}
    resp = httpx.post(_LEADS_URL, headers=headers, json=body, timeout=15)
    resp.raise_for_status()
```

- [ ] **Step 6: Correr los tests, verificar que pasan**

Run: `pytest tests/test_tools_zoho.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add sol-de-oro-concierge/backend/app/tools/zoho.py sol-de-oro-concierge/backend/app/config/settings.py sol-de-oro-concierge/backend/.env.example sol-de-oro-concierge/backend/tests/test_tools_zoho.py
git commit -m "feat(concierge): add Zoho CRM Self Client and create_lead_from_capture"
```

---

### Task 7: `app/tools/mail.py` — notificación de reserva de restaurante

**Files:**
- Create: `sol-de-oro-concierge/backend/app/tools/mail.py`
- Modify: `sol-de-oro-concierge/backend/.env.example`
- Test: `sol-de-oro-concierge/backend/tests/test_tools_mail.py`

**Interfaces:**
- Consumes: `settings.hostinger_mail_token` (agregado en Task 6).
- Produces: `mail.is_configured() -> bool`, `mail.send_reservation_notification(lead: dict) -> None` — consumido por Task 8.

**Nota sobre el contrato de la API**: verificado en vivo contra la API de correo de Hostinger (`GET /api/v1/me` para descubrir el `resourceId` del mailbox, `POST /api/v1/mailboxes/{resourceId}/send` para enviar — devuelve `204` sin body en éxito). Base URL: `https://api.mail.hostinger.com`. Auth: header `Authorization: Bearer <token>`.

- [ ] **Step 1: Escribir el test que falla**

`tests/test_tools_mail.py`:

```python
import app.tools.mail as mail_module
from app.tools.mail import is_configured, send_reservation_notification


class _FakeResponse:
    def __init__(self, json_body=None, status_code=200):
        self._json = json_body or {}
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._json


def test_is_configured_false_without_token(monkeypatch):
    monkeypatch.setattr(mail_module.settings, "hostinger_mail_token", None)
    assert is_configured() is False


def test_is_configured_true_with_token(monkeypatch):
    monkeypatch.setattr(mail_module.settings, "hostinger_mail_token", "some-token")
    assert is_configured() is True


def test_send_reservation_notification_resolves_mailbox_then_sends(monkeypatch):
    monkeypatch.setattr(mail_module.settings, "hostinger_mail_token", "some-token")
    mail_module._cached_resource_id.clear()

    calls = []

    def fake_get(url, **kwargs):
        calls.append(("GET", url, kwargs))
        return _FakeResponse({"data": {"mailboxes": [
            {"resourceId": "AC123", "address": "reservas@soldeoro.pe"},
            {"resourceId": "AC999", "address": "otro@soldeoro.pe"},
        ]}})

    def fake_post(url, **kwargs):
        calls.append(("POST", url, kwargs))
        return _FakeResponse(status_code=204)

    monkeypatch.setattr(mail_module.httpx, "get", fake_get)
    monkeypatch.setattr(mail_module.httpx, "post", fake_post)

    send_reservation_notification({
        "name": "Carla Ruiz", "phone": "+51988888888", "event_type": "Mesa",
        "event_date": "22 de agosto", "time": "8:30pm", "guests": 4,
    })

    method, url, kwargs = calls[1]
    assert method == "POST"
    assert url == "https://api.mail.hostinger.com/api/v1/mailboxes/AC123/send"
    assert kwargs["json"]["to"] == ["reservas@soldeoro.pe"]
    assert "Carla Ruiz" in kwargs["json"]["text"]
    assert "8:30pm" in kwargs["json"]["text"]
    assert kwargs["headers"]["Authorization"] == "Bearer some-token"


def test_send_reservation_notification_reuses_cached_resource_id(monkeypatch):
    monkeypatch.setattr(mail_module.settings, "hostinger_mail_token", "some-token")
    mail_module._cached_resource_id.clear()

    get_calls = []

    def fake_get(url, **kwargs):
        get_calls.append(url)
        return _FakeResponse({"data": {"mailboxes": [{"resourceId": "AC123", "address": "reservas@soldeoro.pe"}]}})

    def fake_post(url, **kwargs):
        return _FakeResponse(status_code=204)

    monkeypatch.setattr(mail_module.httpx, "get", fake_get)
    monkeypatch.setattr(mail_module.httpx, "post", fake_post)

    send_reservation_notification({"name": "A"})
    send_reservation_notification({"name": "B"})

    assert len(get_calls) == 1
```

- [ ] **Step 2: Correr los tests, verificar que fallan**

Run: `pytest tests/test_tools_mail.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.tools.mail'`

- [ ] **Step 3: Implementar `app/tools/mail.py`**

```python
import httpx

from app.config.settings import settings

_BASE_URL = "https://api.mail.hostinger.com"
# reservas@soldeoro.pe es el único email real ya verificado para reservas en el código
# existente (ver _ALLOWED_EMAILS en concierge.py) — se reutiliza como destino Y origen de
# la notificación, así no hace falta una casilla dedicada nueva.
_MAILBOX_ADDRESS = "reservas@soldeoro.pe"

_cached_resource_id: dict = {}


def is_configured() -> bool:
    return bool(settings.hostinger_mail_token)


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.hostinger_mail_token}", "Content-Type": "application/json"}


def _get_mailbox_resource_id() -> str:
    if _cached_resource_id.get("id"):
        return _cached_resource_id["id"]
    resp = httpx.get(f"{_BASE_URL}/api/v1/me", headers=_headers(), timeout=15)
    resp.raise_for_status()
    mailboxes = resp.json()["data"]["mailboxes"]
    match = next((m for m in mailboxes if m["address"] == _MAILBOX_ADDRESS), None)
    if match is None:
        raise RuntimeError(f"No se encontró el mailbox {_MAILBOX_ADDRESS} en la cuenta de Hostinger configurada")
    _cached_resource_id["id"] = match["resourceId"]
    return _cached_resource_id["id"]


def send_reservation_notification(lead: dict) -> None:
    resource_id = _get_mailbox_resource_id()
    lines = [
        f"Tipo: {lead.get('event_type', '(no especificado)')}",
        f"Nombre: {lead.get('name', '(no especificado)')}",
        f"Contacto: {lead.get('email') or lead.get('phone') or '(no especificado)'}",
        f"Fecha: {lead.get('event_date', '(no especificada)')}",
        f"Hora: {lead.get('time', '(no especificada)')}",
        f"Personas: {lead.get('guests', '(no especificado)')}",
        f"Comentarios: {lead.get('requirements', '(ninguno)')}",
    ]
    body_text = "Solicitud de reserva recibida por el Concierge virtual:\n\n" + "\n".join(lines)
    resp = httpx.post(
        f"{_BASE_URL}/api/v1/mailboxes/{resource_id}/send",
        headers=_headers(),
        json={"to": [_MAILBOX_ADDRESS], "subject": "Nueva solicitud de reserva — Restaurante", "text": body_text},
        timeout=15,
    )
    resp.raise_for_status()
```

- [ ] **Step 4: Correr los tests, verificar que pasan**

Run: `pytest tests/test_tools_mail.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add sol-de-oro-concierge/backend/app/tools/mail.py sol-de-oro-concierge/backend/.env.example sol-de-oro-concierge/backend/tests/test_tools_mail.py
git commit -m "feat(concierge): add Hostinger Mail notification for restaurant reservations"
```

---

### Task 8: `_persist_lead` — enchufar Zoho y la notificación de restaurante

**Files:**
- Modify: `sol-de-oro-concierge/backend/app/api/concierge.py`
- Modify: `sol-de-oro-concierge/backend/tests/test_events_and_leads.py`

**Interfaces:**
- Consumes: `zoho.is_configured()`, `zoho.create_lead_from_capture(lead)` (Task 6); `mail.is_configured()`, `mail.send_reservation_notification(lead)` (Task 7).

- [ ] **Step 1: Escribir los tests que fallan**

Agregar a `tests/test_events_and_leads.py`:

```python
def test_persist_lead_creates_zoho_lead_when_type_is_eventos(monkeypatch):
    monkeypatch.setattr("app.api.concierge.tools.insert_lead", lambda payload: {"id": "fake"})
    zoho_calls = []
    monkeypatch.setattr("app.api.concierge.zoho.is_configured", lambda: True)
    monkeypatch.setattr("app.api.concierge.zoho.create_lead_from_capture", lambda lead: zoho_calls.append(lead))
    mail_calls = []
    monkeypatch.setattr("app.api.concierge.mail.send_reservation_notification", lambda lead: mail_calls.append(lead))

    session = get_session("test-persist-zoho")
    _capture_lead(session, {"name": "Ana", "event_type": "Social", "guests": 50})
    _persist_lead(session, "test-persist-zoho", "eventos")

    assert len(zoho_calls) == 1
    assert zoho_calls[0]["name"] == "Ana"
    assert mail_calls == []


def test_persist_lead_skips_zoho_when_not_configured(monkeypatch):
    monkeypatch.setattr("app.api.concierge.tools.insert_lead", lambda payload: {"id": "fake"})
    monkeypatch.setattr("app.api.concierge.zoho.is_configured", lambda: False)
    zoho_calls = []
    monkeypatch.setattr("app.api.concierge.zoho.create_lead_from_capture", lambda lead: zoho_calls.append(lead))

    session = get_session("test-persist-zoho-unconfigured")
    _capture_lead(session, {"name": "Ana", "event_type": "Social"})
    _persist_lead(session, "test-persist-zoho-unconfigured", "eventos")  # no debe lanzar

    assert zoho_calls == []
    assert session["lead"].get("_persisted") is True  # el lead igual quedó en Supabase


def test_persist_lead_sends_mail_when_type_is_restaurante(monkeypatch):
    monkeypatch.setattr("app.api.concierge.tools.insert_lead", lambda payload: {"id": "fake"})
    monkeypatch.setattr("app.api.concierge.zoho.is_configured", lambda: True)
    zoho_calls = []
    monkeypatch.setattr("app.api.concierge.zoho.create_lead_from_capture", lambda lead: zoho_calls.append(lead))
    monkeypatch.setattr("app.api.concierge.mail.is_configured", lambda: True)
    mail_calls = []
    monkeypatch.setattr("app.api.concierge.mail.send_reservation_notification", lambda lead: mail_calls.append(lead))

    session = get_session("test-persist-mail")
    _capture_lead(session, {"name": "Carla", "event_type": "Mesa", "event_date": "22 de agosto", "time": "8pm", "guests": 4})
    _persist_lead(session, "test-persist-mail", "restaurante")

    assert len(mail_calls) == 1
    assert mail_calls[0]["name"] == "Carla"
    assert zoho_calls == []


def test_persist_lead_survives_zoho_failure(monkeypatch):
    monkeypatch.setattr("app.api.concierge.tools.insert_lead", lambda payload: {"id": "fake"})
    monkeypatch.setattr("app.api.concierge.zoho.is_configured", lambda: True)

    def _boom(lead):
        raise RuntimeError("zoho caído")

    monkeypatch.setattr("app.api.concierge.zoho.create_lead_from_capture", _boom)

    session = get_session("test-persist-zoho-fail")
    _capture_lead(session, {"name": "Ana", "event_type": "Social"})
    _persist_lead(session, "test-persist-zoho-fail", "eventos")  # no debe lanzar

    assert session["lead"].get("_persisted") is True  # Supabase sí se guardó
```

- [ ] **Step 2: Correr los tests, verificar que fallan**

Run: `pytest tests/test_events_and_leads.py -v`
Expected: FAIL — `AttributeError: module 'app.api.concierge' has no attribute 'zoho'`

- [ ] **Step 3: Importar `zoho` y `mail` en `concierge.py`**

Reemplazar:

```python
from app.llm.nvidia_client import chat, chat_stream
from app.session import append_message, get_session, save_session
from app.tools import supabase as tools
```

por:

```python
from app.llm.nvidia_client import chat, chat_stream
from app.session import append_message, get_session, save_session
from app.tools import mail, supabase as tools, zoho
```

- [ ] **Step 4: Extender `_persist_lead`**

Reemplazar:

```python
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
```

por:

```python
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
        return

    lead_type = payload["lead_type"]
    # Zoho solo para eventos (spec Fase 3, decisión 1 — restaurante no toca el CRM). Fallos
    # de Zoho (token vencido, rate limit) se loguean y nunca tumban la respuesta al huésped —
    # el lead ya quedó a salvo en Supabase igual.
    if lead_type == "eventos" and zoho.is_configured():
        try:
            zoho.create_lead_from_capture(lead)
        except Exception:
            logger.exception("Fallo al crear lead en Zoho CRM (session_id=%s)", session_id)
    elif lead_type == "restaurante" and mail.is_configured():
        try:
            mail.send_reservation_notification(lead)
        except Exception:
            logger.exception("Fallo al enviar notificación de reserva de restaurante (session_id=%s)", session_id)
```

- [ ] **Step 5: Correr los tests, verificar que pasan**

Run: `pytest tests/test_events_and_leads.py -v`
Expected: PASS (todos, incluidos los de Fase 1)

- [ ] **Step 6: Correr toda la suite del backend**

Run: `pytest tests/ -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add sol-de-oro-concierge/backend/app/api/concierge.py sol-de-oro-concierge/backend/tests/test_events_and_leads.py
git commit -m "feat(concierge): wire Zoho lead creation and restaurant mail notification into _persist_lead"
```

---

### Task 9: Guardrail — contenido prohibido

**Files:**
- Modify: `sol-de-oro-concierge/backend/app/api/concierge.py`
- Test: `sol-de-oro-concierge/backend/tests/test_prohibited_content.py`

**Interfaces:**
- Produces: `_is_prohibited_content(message: str) -> bool`, `_PROHIBITED_MESSAGE: str` — ya referenciados por el endpoint desde la Task 4 (Step 7/8); este task los implementa de verdad.

- [ ] **Step 1: Escribir el test que falla**

`tests/test_prohibited_content.py`:

```python
from fastapi.testclient import TestClient

from app.api.concierge import _is_prohibited_content, _PROHIBITED_MESSAGE
from app.main import app

client = TestClient(app)


def test_detects_common_variants():
    assert _is_prohibited_content("¿tienen prostitutas?") is True
    assert _is_prohibited_content("busco un escort para esta noche") is True
    assert _is_prohibited_content("necesito una dama de compañía") is True
    assert _is_prohibited_content("¿hay chicas de compañía en el hotel?") is True


def test_does_not_flag_unrelated_messages():
    assert _is_prohibited_content("¿tienen piscina?") is False
    assert _is_prohibited_content("quiero reservar una habitación para mi esposa y mis hijos") is False


def test_endpoint_returns_fixed_message_without_calling_llm(monkeypatch):
    def _boom(*args, **kwargs):
        raise AssertionError("no debería llamarse al LLM para contenido prohibido")

    monkeypatch.setattr("app.api.concierge.chat", _boom)
    response = client.post("/api/concierge", json={"message": "¿ofrecen servicios de escort?", "session_id": "test-prohibited-1"})
    assert response.status_code == 200
    assert response.json()["message"] == _PROHIBITED_MESSAGE


def test_stream_endpoint_returns_fixed_message_without_calling_llm(monkeypatch):
    def _boom(*args, **kwargs):
        raise AssertionError("no debería llamarse al LLM para contenido prohibido")

    monkeypatch.setattr("app.api.concierge.chat_stream", _boom)
    response = client.post("/api/concierge/stream", json={"message": "quiero una dama de compañía", "session_id": "test-prohibited-2"})
    assert response.status_code == 200
    assert _PROHIBITED_MESSAGE in response.text
```

- [ ] **Step 2: Correr los tests, verificar que fallan**

Run: `pytest tests/test_prohibited_content.py -v`
Expected: FAIL — `ImportError: cannot import name '_is_prohibited_content'`

- [ ] **Step 3: Implementar el guardrail**

Agregar en `app/api/concierge.py`, cerca de `_FALLBACK_MESSAGE`/`_CONTACT_ACTION`:

```python
# Guardrail determinista: nunca se le pide al modelo que juzgue esto — un 8B puede
# responder de forma inconsistente, y este es justo el tipo de contenido donde no hay
# margen para inconsistencia. Corta ANTES de llamar al LLM, sin tools, sin logging especial
# (decisión explícita del cliente — solo responder y redirigir).
_PROHIBITED_MESSAGE = (
    "Ese tipo de servicio no está permitido ni se ofrece en las instalaciones del Hotel Sol de Oro. "
    "Si tienes alguna otra consulta sobre el hotel, con gusto te ayudo."
)
_PROHIBITED_KEYWORDS = (
    "prostitu", "escort", "acompañante sexual", "dama de compañ", "damas de compañ",
    "chica de compañ", "chicas de compañ", "señorita de compañ", "servicio sexual",
    "servicios sexuales", "trabajador sexual", "trabajadora sexual", "trabajadoras sexuales",
)


def _is_prohibited_content(message: str) -> bool:
    lowered = message.lower()
    return any(keyword in lowered for keyword in _PROHIBITED_KEYWORDS)
```

- [ ] **Step 4: Enchufar el guardrail en los dos endpoints**

Esto modifica el mismo `concierge()`/`concierge_stream()` que dejó la Task 4 — agrega el corte temprano, no cambia nada más de esas funciones.

Reemplazar el inicio de `concierge()`:

```python
@router.post("/api/concierge", response_model=ConciergeResponse)
def concierge(payload: ConciergeRequest) -> ConciergeResponse:
    session = get_session(payload.session_id)
    if payload.page_context:
        session["page_context"] = payload.page_context
    append_message(session, "user", payload.message)
```

por:

```python
@router.post("/api/concierge", response_model=ConciergeResponse)
def concierge(payload: ConciergeRequest) -> ConciergeResponse:
    if _is_prohibited_content(payload.message):
        return ConciergeResponse(message=_PROHIBITED_MESSAGE, intent="PROHIBITED", actions=[])

    session = get_session(payload.session_id)
    if payload.page_context:
        session["page_context"] = payload.page_context
    append_message(session, "user", payload.message)
```

Reemplazar `concierge_stream()`:

```python
@router.post("/api/concierge/stream")
def concierge_stream(payload: ConciergeRequest) -> StreamingResponse:
    session = get_session(payload.session_id)
    return StreamingResponse(_stream_concierge_turn(payload, session), media_type="text/event-stream")
```

por:

```python
@router.post("/api/concierge/stream")
def concierge_stream(payload: ConciergeRequest) -> StreamingResponse:
    if _is_prohibited_content(payload.message):
        def _one_shot():
            yield _sse_event({"type": "chunk", "text": _PROHIBITED_MESSAGE})
            yield _sse_event({"type": "done"})
        return StreamingResponse(_one_shot(), media_type="text/event-stream")
    session = get_session(payload.session_id)
    return StreamingResponse(_stream_concierge_turn(payload, session), media_type="text/event-stream")
```

- [ ] **Step 5: Correr los tests, verificar que pasan**

Run: `pytest tests/test_prohibited_content.py -v`
Expected: PASS

- [ ] **Step 6: Correr toda la suite del backend**

Run: `pytest tests/ -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add sol-de-oro-concierge/backend/app/api/concierge.py sol-de-oro-concierge/backend/tests/test_prohibited_content.py
git commit -m "feat(concierge): add deterministic guardrail for prohibited content"
```

---

### Task 10: `concierge.js` — URLs relativas + widget proactivo en Eventos/Restaurante

**Files:**
- Modify: `sol-de-oro-concierge/frontend/widget/concierge.js`

**Interfaces:**
- Produces: el widget manda `page_context` en el body de cada request al backend (consumido por `ConciergeRequest.page_context`, Task 4).

- [ ] **Step 1: Cambiar las URLs del backend a rutas relativas**

Reemplazar:

```javascript
const API_URL = "http://localhost:8001/api/concierge";
const STREAM_URL = "http://localhost:8001/api/concierge/stream";
```

por:

```javascript
const API_URL = "/api/concierge";
const STREAM_URL = "/api/concierge/stream";
```

- [ ] **Step 2: Detectar el contexto de página**

Agregar después de la declaración de `PERSONAS`/`pickRandomPersona` (antes de `let sessionId = ...`):

```javascript
// Contexto de página: el backend usa esto para priorizar las preguntas calificadoras
// correctas desde el primer turno (ver _PAGE_CONTEXT_HINTS en concierge.py), y el frontend
// lo usa para decidir si abre el panel solo con un saludo distinto (ver setPanelOpen).
const PAGE_CONTEXT_GREETINGS = {
  eventos: (p) => `¡Hola! Soy ${p.name}, Concierge Virtual del Hotel Sol de Oro. Veo que estás en Eventos — ¿te ayudo a cotizar tu evento social o corporativo? Cuéntame qué tipo de evento es, la fecha aproximada, y cuántas personas.`,
  restaurante: (p) => `¡Hola! Soy ${p.name}, Concierge Virtual del Hotel Sol de Oro. ¿Quieres reservar una mesa o el desayuno buffet? Cuéntame el día, la hora y para cuántas personas, y te dejo la solicitud lista para el equipo del hotel.`,
};

function detectPageContext() {
  const path = window.location.pathname.toLowerCase();
  if (path.includes("eventos")) return "eventos";
  if (path.includes("restaurante")) return "restaurante";
  return null;
}
const pageContext = detectPageContext();
```

- [ ] **Step 3: Usar el saludo contextual en `buildGreeting`**

Reemplazar:

```javascript
function buildGreeting(p) {
  return `¡Hola! Soy ${p.name}, Concierge Virtual del Hotel Sol de Oro. ¿Con quién tengo el gusto, y ya eres huésped del hotel o nos estás conociendo? Cuéntame también en qué te puedo ayudar.`;
}
```

por:

```javascript
function buildGreeting(p) {
  const contextual = PAGE_CONTEXT_GREETINGS[pageContext];
  if (contextual) return contextual(p);
  return `¡Hola! Soy ${p.name}, Concierge Virtual del Hotel Sol de Oro. ¿Con quién tengo el gusto, y ya eres huésped del hotel o nos estás conociendo? Cuéntame también en qué te puedo ayudar.`;
}
```

- [ ] **Step 4: Abrir el panel solo la primera vez, en Eventos/Restaurante**

Ubicar este bloque (ya existente, cerca del final de la sección "Restaurar sesión previa"):

```javascript
if (sessionStorage.getItem(SS_OPEN) === "1") {
  panel.classList.add("open");
}

function setPanelOpen(open) {
```

y agregar, justo antes de `function setPanelOpen(open) {`:

```javascript
// Apertura proactiva: solo en Eventos/Restaurante, solo la primera vez de la sesión (nunca
// saludó todavía y no hay conversación restaurada de otra página). Los <form> estáticos de
// esas páginas se quedan intactos — esto es un canal alternativo, no un reemplazo.
if (pageContext && !hasGreeted && storedMessages.length === 0) {
  setTimeout(() => setPanelOpen(true), 2500);
}
```

- [ ] **Step 5: Mandar `page_context` en el body de ambos fetch de `send()`**

Reemplazar (dentro de `send()`, la llamada a `STREAM_URL`):

```javascript
    const resp = await fetch(STREAM_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId, persona: persona.key }),
    });
```

por:

```javascript
    const resp = await fetch(STREAM_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId, persona: persona.key, page_context: pageContext }),
    });
```

y, en el bloque `catch` de `send()`, reemplazar la llamada a `API_URL`:

```javascript
      const resp = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: sessionId, persona: persona.key }),
      });
```

por:

```javascript
      const resp = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: sessionId, persona: persona.key, page_context: pageContext }),
      });
```

- [ ] **Step 6: Verificación manual en navegador**

No hay suite de tests de frontend en este proyecto — verificar a mano:
1. Levantar el backend local (`uvicorn app.main:app --reload --port 8001` desde `sol-de-oro-concierge/backend`, con CORS todavía apuntando a `localhost:8000`/`8080` — esto se resuelve en la Task 13, por ahora se prueba sirviendo el sitio en un puerto local permitido).
2. Servir el sitio (`python -m http.server 8000` desde la raíz del repo) y abrir `http://localhost:8000/eventos.html`.
3. Confirmar: el panel se abre solo a los ~2.5s con el saludo de eventos; escribir un mensaje y confirmar que llega respuesta (usa `API_URL`/`STREAM_URL` relativos, que en este servidor local resuelven a `http://localhost:8000/api/concierge` — **esperado que falle** en este paso porque el sitio estático no sirve `/api/*` todavía; esto se resuelve recién con el deploy real de la Task 13. Lo que se verifica ACÁ es solo: 1) el panel se abre solo, 2) el saludo es el correcto para la página, 3) la consola del navegador no tira errores de JS antes del fetch).
4. Repetir en `http://localhost:8000/restaurante.html` — saludo de restaurante.
5. Repetir en `http://localhost:8000/index.html` — el panel NO debe abrirse solo (sin `pageContext`).

- [ ] **Step 7: Commit**

```bash
git add sol-de-oro-concierge/frontend/widget/concierge.js
git commit -m "feat(concierge): relative API URLs, proactive open and page_context on eventos/restaurante"
```

---

### Task 11: Retirar la CSP temporal de Fase 1 de las 14 páginas

**Files:**
- Modify: `index.html`, `habitaciones.html`, `eventos.html`, `restaurante.html`, `servicios.html`, `experiencias.html`, `ofertas.html`, `faq.html`, `galeria.html`, `ubicacion.html`, `acerca.html`, `empresarial.html`, `privacidad.html`, `terminos.html`

**Interfaces:**
- Ninguna — cambio de contenido estático, no afecta código.

- [ ] **Step 1: Confirmar el patrón exacto en cada archivo**

En cada uno de los 14 archivos, ubicar el bloque (el `connect-src` exacto varía por página — algunas incluyen `https://formspree.io`, otras no; eso no importa para este paso):

```html
<!-- CSP con connect-src ampliado a localhost:8001 SOLO para probar el AI Concierge en local (Fase 1).
     Quitar "http://localhost:8001" antes de desplegar a producción — la integración real del
     widget con su dominio final es trabajo de Fase 3/4, no de esta prueba. -->
<meta http-equiv="Content-Security-Policy" content="..." />
```

- [ ] **Step 2: Eliminar el bloque completo (comentario + meta tag) en cada uno de los 14 archivos**

No reemplazar por nada — la CSP de producción pasa a vivir únicamente en `vercel.json` (Task 12), mismo origen para el widget, sin necesitar `connect-src` adicional. El resto de los `<meta>` de seguridad que están justo después (`X-Content-Type-Options`, `referrer`, etc.) se dejan intactos — no forman parte de este bloque temporal.

- [ ] **Step 3: Verificar que no queda ninguna referencia**

Run: `grep -rl "CSP con connect-src ampliado" *.html`
Expected: sin resultados (ninguna coincidencia)

Run: `grep -rl "localhost:8001" *.html`
Expected: sin resultados

- [ ] **Step 4: Commit**

```bash
git add index.html habitaciones.html eventos.html restaurante.html servicios.html experiencias.html ofertas.html faq.html galeria.html ubicacion.html acerca.html empresarial.html privacidad.html terminos.html
git commit -m "chore(site): remove temporary Fase-1 CSP meta tag from all pages"
```

---

### Task 12: Configuración de Vercel — `api/index.py`, `requirements.txt`, `vercel.json`, `.vercelignore`

**Files:**
- Create: `api/index.py`
- Create: `requirements.txt` (raíz del repo)
- Create: `vercel.json` (raíz del repo)
- Create: `.vercelignore` (raíz del repo)

**Interfaces:**
- Produces: función serverless en `/api/*` que sirve la app FastAPI existente (`sol-de-oro-concierge/backend/app/main.py`), sin duplicar su código fuente.

- [ ] **Step 1: Crear `api/index.py`**

```python
import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent / "sol-de-oro-concierge" / "backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.main import app  # noqa: E402
```

- [ ] **Step 2: Crear `requirements.txt` en la raíz (copia de `sol-de-oro-concierge/backend/requirements.txt`)**

```text
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic-settings==2.6.1
httpx==0.27.2
openai==1.54.0
pytest==8.3.3
pytest-asyncio==0.24.0
```

Nota: mantener sincronizado a mano con `sol-de-oro-concierge/backend/requirements.txt` cuando se agregue una dependencia nueva — este archivo existe solo porque Vercel necesita `requirements.txt` en la raíz del proyecto para detectar la función Python; el de `backend/` sigue siendo el que se usa para desarrollo local.

- [ ] **Step 3: Crear `vercel.json`**

```json
{
  "cleanUrls": true,
  "trailingSlash": false,
  "functions": {
    "api/index.py": {
      "includeFiles": "sol-de-oro-concierge/backend/**"
    }
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(self), payment=(self), usb=(), interest-cohort=()" },
        { "key": "Content-Security-Policy", "value": "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com data:; connect-src 'self' https://*.supabase.co https://*.tile.openstreetmap.org https://*.cartocdn.com https://soldeoro.ihotelier.com https://formspree.io; frame-src 'self' https://www.google.com https://maps.google.com; form-action 'self' https://soldeoro.ihotelier.com mailto:; frame-ancestors 'none'; base-uri 'self'; object-src 'none'; upgrade-insecure-requests" },
        { "key": "Cross-Origin-Opener-Policy", "value": "same-origin" },
        { "key": "Cross-Origin-Resource-Policy", "value": "same-origin" }
      ]
    }
  ]
}
```

- [ ] **Step 4: Crear `.vercelignore`**

```text
sol-de-oro-concierge/backend/.env
sol-de-oro-concierge/backend/.venv
sol-de-oro-concierge/backend/.pytest_cache
sol-de-oro-concierge/backend/tests
sol-de-oro-concierge/backend/diag_instalaciones.txt
sol-de-oro-concierge/backend/diag_instalaciones2.txt
sol-de-oro-concierge/backend/full_run_final.txt
sol-de-oro-concierge/migrations
editor-imagenes.html
docs
admin/*.sql
_backup
.git
.claude
node_modules
```

- [ ] **Step 5: Commit**

```bash
git add api/index.py requirements.txt vercel.json .vercelignore
git commit -m "feat(deploy): add unified Vercel config for site + concierge backend"
```

---

### Task 13: Deploy a Vercel, verificación, y guía de credenciales de Zoho

**Files:**
- Ninguno de código — este task es operativo (deploy real + documentación entregada al usuario).

- [ ] **Step 1: Cargar las variables de entorno en el proyecto Vercel**

Usando `VERCEL_TOKEN` (ya en `sol-de-oro-concierge/backend/.env`), desde la raíz del repo:

```bash
export VERCEL_TOKEN=$(grep VERCEL_TOKEN sol-de-oro-concierge/backend/.env | cut -d= -f2)
npx vercel link --token "$VERCEL_TOKEN" --yes
npx vercel env add SUPABASE_URL production --token "$VERCEL_TOKEN"
npx vercel env add SUPABASE_ANON_KEY production --token "$VERCEL_TOKEN"
npx vercel env add NVIDIA_API_KEY production --token "$VERCEL_TOKEN"
npx vercel env add NVIDIA_BASE_URL production --token "$VERCEL_TOKEN"
```

(Los valores se toman de `sol-de-oro-concierge/backend/.env` — cada comando pide el valor por stdin de forma interactiva; si se ejecuta en un entorno no interactivo, usar `npx vercel env add <NAME> production <<< "<value>"`.) Las variables de Zoho y Hostinger Mail se agregan recién cuando el usuario las entregue (Step 4 de este task) — no bloquean el deploy: `zoho.is_configured()`/`mail.is_configured()` devuelven `False` sin ellas y el resto del sistema sigue funcionando.

- [ ] **Step 2: Deploy**

```bash
npx vercel --prod --token "$VERCEL_TOKEN"
```

Expected: output con una URL `https://<algo>.vercel.app`.

- [ ] **Step 3: Verificar el deploy**

```bash
curl -s https://<la-url-real>.vercel.app/health
# Expected: {"status":"ok"}

curl -s -X POST https://<la-url-real>.vercel.app/api/concierge \
  -H "Content-Type: application/json" \
  -d '{"message":"¿qué habitaciones tienen?","session_id":"vercel-smoke-test-1"}'
# Expected: JSON con "message" no vacío, mencionando datos reales de habitaciones

curl -s -o /dev/null -w "%{http_code}\n" https://<la-url-real>.vercel.app/editor-imagenes.html
# Expected: 404

curl -s -o /dev/null -w "%{http_code}\n" https://<la-url-real>.vercel.app/sol-de-oro-concierge/backend/app/api/concierge.py
# Expected: 404
```

**Si el último check devuelve 200 en vez de 404** (el código fuente del backend queda públicamente descargable): el `includeFiles` de `vercel.json` está haciendo que Vercel también sirva ese directorio como estático, no solo como dependencia de la función. Fallback concreto: mover `sol-de-oro-concierge/backend/app/` a `api/_backend/app/` (dentro de `/api/`, que Vercel nunca sirve como estático), actualizar el `sys.path.insert` de `api/index.py` para apuntar ahí, y quitar la entrada `sol-de-oro-concierge/backend/**` de `.vercelignore`. Repetir el deploy y volver a correr este check.

Abrir `https://<la-url-real>.vercel.app/eventos.html` en un navegador real y confirmar: el widget abre solo con el saludo de eventos, y una pregunta real obtiene respuesta (ahora sí, mismo origen — a diferencia del check manual de la Task 10).

- [ ] **Step 4: Guía para el usuario — generar el Self Client de Zoho**

Entregar estas instrucciones (no ejecutables por el asistente, requieren login del usuario en su cuenta Zoho con permisos de admin del org `org923571984`):

1. Entrar a [api-console.zoho.com](https://api-console.zoho.com) con la cuenta admin del org.
2. "Add Client" → **Self Client**.
3. En la pestaña "Generate Code": scope `ZohoCRM.modules.leads.CREATE,ZohoCRM.modules.leads.READ`, tiempo de expiración del código (el máximo disponible, ej. 10 minutos), "Create".
4. Copiar el `client_id` y `client_secret` que aparecen en la pestaña "Client Secret" del Self Client recién creado.
5. Con el código generado en el paso 3 (dura pocos minutos, hay que usarlo rápido), hacer un POST manual para obtener el primer refresh token:
   ```bash
   curl -X POST https://accounts.zoho.com/oauth/v2/token \
     -d "code=<el_codigo_del_paso_3>" \
     -d "client_id=<client_id>" \
     -d "client_secret=<client_secret>" \
     -d "grant_type=authorization_code"
   ```
   La respuesta incluye `refresh_token` — esto es lo único de esta lista que no expira solo (dura hasta que se revoque manualmente).
6. Guardar los tres valores (`client_id`, `client_secret`, `refresh_token`) en `sol-de-oro-concierge/backend/.env` como `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN` — igual que se hizo con `VERCEL_TOKEN`.
7. Avisar al asistente cuando estén cargados — el siguiente paso es correr `npx vercel env add ZOHO_CLIENT_ID production` (y lo mismo para los otros dos) contra el proyecto ya desplegado, y confirmar con Gerencia General el valor de `Fuente_Original` pendiente (spec, "Puntos abiertos" #1) antes de dejar la escritura activa contra el org de producción.

- [ ] **Step 5: Guía para el usuario — token de la API de correo de Hostinger**

1. Entrar al panel de Hostinger, sección de la cuenta de correo que administra `reservas@soldeoro.pe`.
2. Generar un API token con acceso de envío (`Send`) sobre ese mailbox — la ubicación exacta depende de si `soldeoro.pe` está bajo el mismo panel de hPanel que ya usás para otras cosas del hotel; si no aparece la opción, es porque esa casilla vive en una cuenta de Hostinger distinta a la conectada en este entorno (confirmado: la conexión de Hostinger Email disponible en esta sesión resuelve a `patrick.bittig@aittro.com`, no a `soldeoro.pe`) — en ese caso hay que generarlo desde la cuenta de Hostinger correcta.
3. Guardar el valor en `.env` como `HOSTINGER_MAIL_TOKEN`.
4. Avisar al asistente — se carga en Vercel igual que las variables de Zoho.

- [ ] **Step 6: No hay commit en este task** (es despliegue + coordinación con el usuario, no cambios de código nuevos).

---

## Verificación final del plan completo

Con las 13 tasks terminadas:
- `pytest tests/ -v` (desde `sol-de-oro-concierge/backend/`) pasa completo.
- El sitio en la URL de Vercel responde igual que en local, sin CORS, con CSP sirviéndose desde `vercel.json`.
- Un lead de eventos capturado en `eventos.html` aparece en Supabase (`concierge_leads`) siempre, y en Zoho (`Posibles clientes`) apenas se carguen las credenciales.
- Una reserva de restaurante capturada en `restaurante.html` aparece en Supabase y genera un email real a `reservas@soldeoro.pe` apenas se cargue `HOSTINGER_MAIL_TOKEN`.
- Un mensaje sobre contenido prohibido devuelve el mensaje fijo sin invocar al modelo, en ambas páginas y en cualquier otra del sitio (el guardrail no depende de `page_context`).
- El corte de DNS real (`soldeoro.com.pe` → Vercel) queda como decisión del usuario, fuera de este plan (spec, "Explícitamente fuera de alcance").
