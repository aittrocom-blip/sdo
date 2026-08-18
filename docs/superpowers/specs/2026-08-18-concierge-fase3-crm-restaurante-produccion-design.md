# Sol de Oro AI Concierge — Fase 3: CRM, Restaurante, Producción y Guardrails

**Fecha:** 2026-08-18
**Estado:** Diseño — pendiente de revisión del usuario antes del plan de implementación
**Precede a este documento:** [2026-08-12-concierge-fase1-prototipo-design.md](2026-08-12-concierge-fase1-prototipo-design.md) (Fase 1 — prototipo con datos reales de Supabase, sin reservas ni integración con Zoho ni producción)

## Contexto

El sitio nuevo del Hotel Sol de Oro (este repositorio) va a **reemplazar por completo** el sitio actualmente en vivo en `soldeoro.com.pe`. El AI Concierge (Fase 1) ya responde preguntas con datos reales y ya está incluido en 14 de las 15 páginas HTML del sitio, pero apunta a un backend local (`localhost:8001`) y no tiene ninguna integración de negocio real todavía — la Fase 1 lo dejó explícitamente fuera de alcance ("Reservas reales, integración con iHotelier, integración con Zoho" y "cambios de CSP" quedaron para Fase 3-4).

Esta fase agrega captura real de leads de eventos hacia Zoho CRM, un mini-módulo de reserva de restaurante, presencia proactiva del widget en las páginas comerciales, un guardrail de contenido prohibido, y el despliegue real a producción — unificando sitio + backend en un solo proyecto Vercel bajo `soldeoro.com.pe`.

## Objetivo de esta fase

Que el Concierge deje de ser un prototipo local y pase a operar en producción, generando leads reales (eventos → Zoho CRM; restaurante → notificación directa al hotel), presente en las páginas de eventos y restaurante desde el primer segundo de la visita, y con una regla de contenido dura para consultas sobre servicios prohibidos en el hotel.

**Criterio de éxito:**
- Un lead de eventos capturado por el Concierge aparece como un registro nuevo en el módulo Posibles clientes de Zoho, con los campos mínimos completos.
- Una solicitud de reserva de restaurante genera un correo real a `reservas@soldeoro.pe` con los datos capturados.
- Entrar a `eventos.html` o `restaurante.html` abre el widget solo, con saludo contextual, la primera vez de la sesión.
- Una consulta sobre acompañantes/servicios sexuales recibe la respuesta fija de prohibición, sin pasar por el modelo.
- El sitio completo (páginas + backend del Concierge) responde desde un único dominio de producción en Vercel.

## Decisiones tomadas durante el brainstorm

1. **Zoho CRM solo para eventos, no para restaurante.** El requerimiento Etapa 1 de Zoho (fuente de verdad vigente del CRM, ver skill `zoho-crm-expert`) cubre únicamente el pipeline de Tratos para eventos corporativos/sociales. Crear una línea de negocio de restaurante en Zoho sería un cambio estructural fuera de ese alcance ya autorizado — se evita esa fricción de gobernanza manejando el restaurante 100% fuera de Zoho (Supabase + notificación por email).
2. **El código que escribe a Zoho es un servicio automatizado, no una acción manual del consultor.** La regla de "el consultor externo nunca crea/edita/borra un registro de cliente" (convención del proyecto Sol de Oro) aplica a acciones manuales vía UI/MCP con datos reales de clientes — no a diseñar e implementar un canal de captura automatizado, que es exactamente lo que `docs/AUDIT.md` §8.4 ya recomendaba (unificar el Action Agent del Concierge con el pipeline de leads de Zoho).
3. **Ampliar `capture_lead`/`_persist_lead` en vez de construir un flujo paralelo.** Ya existen en `concierge.py` (Fase 1): acumulan datos en `session["lead"]` y persisten una fila en Supabase en el momento del handoff. Se extienden con un paso de escritura a Zoho (si `lead_type == "eventos"`) y uno de notificación por email (si `lead_type == "restaurante"`), en vez de crear tools nuevas duplicadas.
4. **Deduplicación de leads de Zoho: nativa por email**, igual que las otras 4 fuentes de leads del hotel (Meta, TikTok, Web, Email) — sin lógica propia de fuzzy-matching.
5. **Widget proactivo, no dependiente de un formulario.** En `eventos.html`/`restaurante.html` el widget se abre solo con saludo contextual la primera vez de la sesión (no espera a que el usuario escriba). Los `<form>` estáticos existentes de esas páginas se dejan intactos como alternativa para quien prefiera no chatear.
6. **Guardrail de contenido prohibido: determinista, no delegado al LLM.** Mismo principio que los guardrails de contacto/links ya existentes en el código (comentario propio: "un 8B no es confiable solo con instrucciones de prompt") — se detecta por palabra clave antes de llamar al modelo y se corta ahí, sin logging especial.
7. **Sesión: de memoria de proceso a una tabla en Supabase.** Requisito no negociable para correr en Vercel (funciones serverless no comparten memoria entre invocaciones, y el frontend solo manda el último mensaje + `session_id`, no el historial completo). De paso resuelve el vacío que `docs/AUDIT.md` §3.4/6.5 ya señalaba (sin persistencia de conversaciones).
8. **Despliegue unificado en Vercel (sitio + backend), no solo el backend.** El sitio actual en `soldeoro.com.pe` va a ser reemplazado de todas formas, así que no hay una producción estable que arriesgar con el cambio de hosting — el corte de DNS iba a pasar igual. Unificar evita CORS/CSP cruzado por completo (el widget llama `/api/concierge` mismo origen) y reemplaza `.htaccess` por `vercel.json` (rewrites de URLs limpias + headers de seguridad, mismo comportamiento). El correo (`reservas@soldeoro.pe`, `comercial@soldeoro.pe`) vive en el dominio separado `soldeoro.pe` y no se toca en absoluto.
9. **Restaurante reutiliza el campo `event_type` para "Mesa"/"Desayuno buffet"** en vez de crear un campo de tipo nuevo, y agrega un campo `time` (hora) que hoy falta en `capture_lead` — necesario para cualquier reserva con horario.

## Arquitectura

```text
Browser (soldeoro.com.pe — sitio + widget, mismo origen)
   │
   ▼ fetch() same-origin
Vercel — un solo proyecto
   ├── /                      (sitio estático: 15 páginas HTML + assets)
   └── /api/concierge         (FastAPI como función serverless)
          │
          ├─▶ NVIDIA Build (NIM, meta/llama-3.1-8b-instruct) — respuesta + function-calling
          ├─▶ Supabase        — datos del hotel (rooms/salons/faq/...), leads, SESIÓN (nueva)
          ├─▶ Zoho CRM API    — solo cuando lead_type == "eventos" (Posibles clientes)
          └─▶ Hostinger Mail API — solo cuando lead_type == "restaurante" (notificación)
```

## Componentes

### 1. Zoho CRM — leads de eventos

`app/tools/zoho.py` (nuevo):
- Cliente OAuth Self Client: refresca el access token con el refresh token (guardado en env vars), cachea el token vigente en la misma tabla de sesión de Supabase con su expiración, para no pedir uno nuevo en cada invocación serverless.
- `create_lead(fields: dict) -> dict`: `POST https://www.zohoapis.com/crm/v2/Leads`, body `{"data": [...], "trigger": ["workflow"]}` (el `trigger` es obligatorio para que dispare la automatización "V5 - SLA WhatsApp" ya activa en el org).

`_persist_lead` (en `concierge.py`, existente) gana un paso condicional:
```text
si lead_type == "eventos":
    zoho.create_lead({
        First_Name / Last_Name  ← lead["name"] (split simple, todo a Last_Name si no hay espacio)
        Email                    ← lead["email"]
        Phone                    ← lead["phone"]
        Tipo_de_consulta         ← "Social" | "Corporativo"  (mapeado desde event_type)
        Fecha_evento_social /
        Fecha_evento_corporativo ← lead["event_date"]  (según Tipo_de_consulta)
        Invitados_evento_social /
        Asistentes_evento_corp   ← lead["guests"]
        Servicios_evento_social /
        Servicios_evento_corp    ← lead["requirements"]
        Fuente_Original          ← PENDIENTE — ver "Puntos abiertos" abajo
    })
```
- Fallos de Zoho (rate limit, token vencido, timeout) se loguean y nunca tumban la respuesta al huésped — mismo patrón que el fallo de Supabase hoy (`_persist_lead` ya envuelve el insert en try/except).
- No se edita, mergea ni borra ningún registro existente — solo creación, siempre.

### 2. Restaurante — mini-módulo de reserva (mesa / desayuno buffet)

- `capture_lead` gana un campo nuevo: `time` (string, hora tal como la dio el huésped).
- El asistente, para `lead_type: "restaurante"`, pide: nombre, contacto (teléfono o email), tipo (**Mesa** o **Desayuno buffet**, guardado en `event_type`), fecha, hora, número de personas.
- `_persist_lead`, para `lead_type == "restaurante"`, además de la fila en Supabase (igual que hoy), llama a `app/tools/mail.py` (nuevo) → `send_notification()` vía la API de correo de Hostinger, a `reservas@soldeoro.pe`, asunto `Nueva solicitud de reserva — Restaurante`, cuerpo con los datos capturados.
- Mensaje al huésped: confirma que la solicitud fue enviada al equipo del hotel y que está **sujeta a confirmación** ("en general hay disponibilidad; el equipo te confirma por WhatsApp o email"), más el link de WhatsApp de siempre como respaldo.
- No toca Zoho — evita crear una línea de negocio no contemplada en el requerimiento Etapa 1.

### 3. Widget proactivo en Eventos y Restaurante

- `concierge.js` detecta la página actual. En `eventos.html`/`restaurante.html`, si no hay `cc_greeted` en `sessionStorage` para esta sesión, abre el panel ~2-3s después de cargar con un saludo contextual por página (distinto texto para eventos vs. restaurante).
- Se manda `page_context` (`"eventos"` | `"restaurante"` | ausente) en el primer mensaje de la sesión, para que el backend priorice las preguntas calificadoras correctas desde el arranque en vez de esperar a que el modelo lo infiera.
- Si el usuario navega entre páginas dentro de la misma sesión, no se reabre solo una segunda vez.
- Los `<form>` estáticos existentes de ambas páginas quedan sin tocar.

### 4. Guardrail — contenido prohibido

- Antes de la llamada al LLM (en el mismo punto donde hoy se arma el payload de `/api/concierge` y `/api/concierge/stream`), se revisa el mensaje del usuario contra una lista de palabras/frases (prostitución, escort, dama de compañía, acompañante con connotación sexual, y variantes comunes).
- Si matchea: se responde directo con un mensaje fijo indicando que ese tipo de servicio está prohibido en las instalaciones del hotel — sin llamar al modelo, sin tools, sin logging especial (por decisión explícita del usuario).
- Mismo principio que los guardrails de contacto/links ya existentes: determinista en código, no una instrucción de prompt que un modelo 8B podría ignorar.

### 5. Sesión — de memoria a Supabase

Nueva tabla `concierge_sessions` (mismo proyecto Supabase, mismo patrón RLS que las demás tablas del Concierge):

```sql
concierge_sessions (
  session_id      text primary key,
  persona         text,
  history         jsonb,      -- turnos de la conversación
  lead            jsonb,      -- lo acumulado por capture_lead
  zoho_token      jsonb,      -- access token cacheado + expiración (evita refrescar en cada invocación)
  created_at      timestamptz,
  updated_at      timestamptz,
  last_activity_at timestamptz
)
```

`app/session.py` cambia sus funciones (`get_session`, `append_message`, etc.) de operar sobre el dict `_SESSIONS` a hacer lecturas/escrituras a esta tabla vía el mismo cliente httpx que ya usa `app/tools/supabase.py`. La lógica de negocio (qué se guarda, cuándo) no cambia — solo dónde vive.

### 6. Despliegue — Vercel unificado

- Un solo proyecto Vercel: el sitio estático completo + `sol-de-oro-concierge/backend` como función serverless bajo `/api/*`.
- `vercel.json` nuevo, reemplaza al `.htaccess` actual:
  - Rewrites para URLs limpias (`/pagina` → `/pagina.html`), igual comportamiento que las reglas RewriteRule actuales.
  - Headers de seguridad (HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, CSP) — el CSP ya no necesita listar un origen externo para `connect-src` del Concierge, porque es mismo origen.
  - Bloqueo de `editor-imagenes.html` (hoy vía `<FilesMatch>` en `.htaccess`) — se replica como regla en `vercel.json` o header `X-Robots-Tag`/`401` según lo que soporte Vercel de forma más directa; se define el mecanismo exacto en el plan de implementación.
- `concierge.js` deja de tener `http://localhost:8001` hardcodeado — pasa a usar rutas relativas (`/api/concierge`, `/api/concierge/stream`).
- CORS del backend deja de ser necesario para el flujo normal del sitio (mismo origen) — se mantiene una configuración mínima solo si hace falta probar el widget desde `concierge.html` standalone en local.
- El corte de DNS real (`soldeoro.com.pe` → Vercel) queda como el último paso, cuando el usuario esté listo para reemplazar el sitio actual — no bloquea el resto de esta fase, que se puede probar contra la URL `*.vercel.app` del proyecto.

## Variables de entorno nuevas

| Variable | Para qué | Quién la genera |
|---|---|---|
| `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN` | Self Client OAuth, escritura de Leads | Usuario, en la API Console de Zoho (org923571984) — guía paso a paso en el plan de implementación |
| `HOSTINGER_MAIL_TOKEN` | Envío de notificación de reserva de restaurante | Usuario, desde el panel de Hostinger |
| `SUPABASE_SERVICE_ROLE_KEY` (a evaluar) | Escritura a `concierge_sessions`/`concierge_leads` si las políticas RLS actuales (público SELECT) no alcanzan para INSERT/UPDATE desde el backend | Se confirma en el plan si la `ANON_KEY` actual ya cubre el caso o hace falta escalar permisos |

Las ya existentes (`NVIDIA_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`) se trasladan tal cual al proyecto Vercel.

## Manejo de errores

- **Zoho no responde / token vencido / rate limit** → se loguea, el lead igual queda guardado en Supabase (ya lo hace hoy), el huésped recibe su respuesta normal sin ninguna mención del fallo interno.
- **Hostinger Mail API falla** → mismo patrón: se loguea, el lead de restaurante queda en Supabase de todas formas, y el mensaje al huésped no cambia (no se le puede prometer que el email llegó si no llegó, pero tampoco se le expone el error — se revisa el log).
- **Supabase no responde para leer/escribir sesión** → ya no es opcional como antes (la sesión no vive en ningún otro lado): fallback a una sesión efímera en memoria de esa sola invocación (sin historial previo) en vez de un 500 crudo, con log de la falla.

## Testing

- Extiende `tests/test_20_questions.py` (Fase 1) con casos nuevos:
  - Flujo completo de captura de lead de eventos → verifica que se llama a `zoho.create_lead` con los campos correctos (mock de la API de Zoho, no contra el org real en tests).
  - Flujo de reserva de restaurante → verifica que se llama a `mail.send_notification` con los datos correctos (mock).
  - Guardrail de contenido prohibido → set de prompts que deben cortar antes del LLM, verificando que nunca se invoca `chat()`/`chat_stream()`.
  - Sesión en Supabase → historial y `lead` sobreviven a una segunda invocación simulando una función serverless nueva (sin estado en memoria compartido).

## Explícitamente fuera de alcance en esta fase

- Verificación de disponibilidad real de mesas/habitaciones — sigue siendo "solicitud sujeta a confirmación del hotel", sin sistema de inventario.
- Edición/actualización de leads existentes en Zoho (solo creación).
- WhatsApp Business API automatizado (Fase 2 según convención del proyecto Zoho).
- Migración completa del sitio actual de `soldeoro.com.pe` con plan de corte de DNS detallado — se deja el mecanismo listo (dominio custom en Vercel), pero la ejecución del corte la decide el usuario cuando esté listo.
- Analítica de conversaciones sobre el historial ahora persistente en Supabase (queda disponible para una fase futura, no se construye dashboard en esta).

## Puntos abiertos — requieren decisión antes de implementar

1. **`Fuente_Original` en Zoho no tiene un valor para "Concierge IA / chat del sitio".** Es un campo obligatorio (convención Etapa 1) y agregar un valor nuevo al picklist es un cambio de estructura del CRM. El código queda listo para mandar el valor que se decida, pero el valor exacto (¿nuevo valor "Concierge IA"? ¿mapear al existente "Tienda en línea/Online Store"?) se confirma con Gerencia General antes de activar la escritura real a Zoho.
2. **Nombre y expiración del token personal de Vercel** y del refresh token de Zoho: se generan durante la implementación, no bloquean este spec.
3. **Mecanismo exacto para bloquear `editor-imagenes.html` en `vercel.json`** (equivalente al `<FilesMatch>` de `.htaccess`) — se resuelve en el plan de implementación, sin impacto en el diseño general.
