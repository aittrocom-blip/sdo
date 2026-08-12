# Sol de Oro AI Concierge — Fase 1: Prototipo

**Fecha:** 2026-08-12
**Estado:** Aprobado, pendiente de plan de implementación
**Precede a este documento:** [AUDIT.md](../../../AUDIT.md) (Fase 0 — auditoría del sitio actual y de Supabase)

## Contexto

El blueprint completo del Sol de Oro AI Concierge (entregado por el usuario) define 5 fases. Este documento cubre **únicamente la Fase 1 — Prototipo**, tratada como su propio sub-proyecto con ciclo diseño → plan → implementación independiente. Las fases 2 (Agentes/NeMo Agent Toolkit), 3 (Actions) y 4 (Deployment) se brainstorman por separado cuando la Fase 1 esté funcionando y validada.

## Objetivo de esta fase

Un endpoint funcionando que reciba una pregunta en lenguaje natural sobre el hotel o Lima, y devuelva una respuesta correcta basada en datos reales de Supabase (nunca inventados), más una UI mínima de chat para probarlo. Sin agentes separados, sin reservas reales, sin integración con el sitio en producción todavía.

**Criterio de éxito:** las 20 preguntas de prueba de la Sección 33 del blueprint, respondidas correctamente contra los datos reales del hotel.

## Decisiones tomadas durante el brainstorm

1. **Inferencia LLM: NVIDIA Build (NIM endpoints)**, no local/Ollama ni Groq/OpenRouter. Encaja con el ecosistema NVIDIA que el blueprint ya exige para Fase 2 (NeMo Agent Toolkit), tiene tier gratuito, y evita mantener dos proveedores de inferencia distintos entre fases.
2. **Migrar contenido a Supabase ahora, no después.** Habitaciones, salones y FAQ viven hoy solo en HTML (hallazgo de AUDIT.md). Antes de programar el router, se migran a tablas nuevas — sin esto, no hay de dónde leer.
3. **"Explorar Lima" se migra a `le_experiences`.** La tabla ya existe con ~40 filas huérfanas (ninguna página pública las lee); se reemplaza su contenido por las 19 tarjetas reales actuales. `experiencias.html` no se reconecta a la tabla en esta fase — es un cambio aparte que no bloquea al Concierge.
4. **Arquitectura de un solo paso** (no pipeline de dos llamadas, no NeMo Agent Toolkit todavía): una llamada al LLM por turno, con function-calling para decidir qué leer de Supabase y redactar la respuesta en el mismo paso. Ver "Approach A" — elegido sobre pipeline de 2 llamadas (más latencia/costo sin beneficio claro) y sobre meter NeMo Agent Toolkit ya (el propio blueprint lo reserva para Fase 2).
5. **Sin Docker en esta fase.** El blueprint lo pide recién en Fase 4 (deployment). Se corre local con `uvicorn` para poder iterar y probar directamente.
6. **Sesión en memoria, no persistente** (dict del proceso, se pierde al reiniciar) — tal como pide la Sección 18 del blueprint para el MVP.

## Arquitectura

```text
Browser (sitio servido local vía python -m http.server, o standalone para pruebas)
   │
   ▼  fetch()
FastAPI  ·  POST /api/concierge
   │
   ▼  1 llamada, structured output (JSON + function-calling)
NVIDIA Build (NIM endpoint — modelo Instruct de la familia Llama 3.x;
               el ID exacto se confirma en el plan de implementación
               contra el catálogo vigente en build.nvidia.com)
   │  el modelo decide qué tool invocar según la pregunta
   ▼
Supabase (rooms, salons, hotel_faq, le_restaurants, le_cultural, le_experiences, offers)
```

## Componentes

```text
sol-de-oro-concierge/
├── backend/
│   ├── app/
│   │   ├── main.py                 -- arranque FastAPI
│   │   ├── api/
│   │   │   └── concierge.py        -- POST /api/concierge
│   │   ├── tools/
│   │   │   └── supabase.py         -- get_rooms(), get_salons(min_pax=None),
│   │   │                              get_faq(topic=None), get_nearby(cat=None),
│   │   │                              get_offers() — funciones tipadas, sin SQL libre
│   │   │                              expuesto al modelo
│   │   ├── llm/
│   │   │   └── nvidia_client.py    -- wrapper del NIM endpoint + function-calling
│   │   ├── session.py              -- dict en memoria {session_id: {history, party, time_available}}
│   │   └── config/
│   │       └── settings.py         -- .env: NVIDIA_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   └── widget/
│       ├── concierge.html          -- página standalone de prueba (no integrada al sitio real todavía)
│       ├── concierge.js            -- botón flotante + panel de chat, vanilla JS
│       └── concierge.css           -- sin Shadow DOM en esta fase (se agrega en Fase 3/4)
│
├── tests/
│   └── test_20_questions.py        -- las 20 preguntas de la Sección 33, contra datos reales
│
└── README.md
```

**Nota sobre el `service_role` de Supabase:** el backend usa `SUPABASE_ANON_KEY` para lectura (mismo patrón RLS que ya usa el resto del sitio: público SELECT). No se usa `service_role` desde este backend salvo que una función de escritura lo requiera explícitamente — y en ese caso, nunca se expone al frontend (Sección 21 del blueprint).

## Modelo de datos — tablas nuevas

Se crean 3 tablas nuevas en el mismo proyecto Supabase (`fjzshpilzjtfjcouzzzz`), mismo patrón de RLS que las tablas existentes (público SELECT, `authenticated` ALL):

```sql
rooms        -- 9 filas, migradas desde habitaciones.html (nombre, categoría, tamaño m²/ft²,
             -- tipo de cama, vista, capacidad, features[], foto)

salons       -- 8 filas, migradas desde la tabla de capacidades de eventos.html
             -- (nombre, capacidad, m², piso, tipos de montaje, notas)

hotel_faq    -- ~30 filas, migradas desde faq.html (sección, pregunta, respuesta)
```

`le_experiences` (ya existe) se actualiza — no se crea de nuevo — reemplazando su contenido por las 19 tarjetas de "Explorar Lima".

No se crean tablas de sesión/analytics en esta fase (Sección 24 del blueprint queda para después — no hay nada que loguear todavía más que lo que ya vive en memoria del proceso).

## Flujo de una request

1. Usuario escribe en el widget → `POST /api/concierge {message, session_id}`.
2. Backend arma el contexto: historial de la sesión (en memoria) + el mensaje nuevo.
3. Una llamada al NIM endpoint con tools declaradas (`get_rooms`, `get_salons`, `get_faq`, `get_nearby`, `get_offers`) y salida estructurada esperada: `{intent, message, actions[]}`.
4. Si el modelo invoca una tool, el backend ejecuta la función contra Supabase, devuelve el resultado al modelo, y el modelo redacta la respuesta final con ese dato real.
5. Backend responde `{message, intent, actions}` al widget.
6. Widget renderiza el mensaje + botones de `actions` (mismo patrón visual que ya usa el sitio: CTAs duales tipo `[Ver experiencia] [Cómo llegar]`).

## Manejo de errores

- **Intención no clara / fuera de dominio** → `intent: OTHER`, respuesta genérica + CTA `[Contactar hotel]` (handoff humano, Sección 20).
- **Supabase no responde** → mensaje hospitalario de error técnico + mismo CTA de contacto. Nunca se inventa el dato faltante (Sección 12).
- **NVIDIA Build falla o rate-limita** → mismo fallback; se loguea para decidir si hace falta un proveedor de respaldo (Groq/OpenRouter quedan como plan B evaluado, no implementado en esta fase).

## Testing

`tests/test_20_questions.py` — las 20 preguntas de ejemplo de la Sección 33 del blueprint (Hotel, Experiencias, Cultura, Compras, Eventos, Reservas), verificando que:
- el `intent` clasificado sea razonable para la pregunta, y
- la respuesta contenga el dato correcto según lo migrado a Supabase (verificación de contenido, no exact-match de texto).

## Explícitamente fuera de alcance en esta fase

- Orchestrator / Hotel Agent / Lima Agent / Action Agent separados (Fase 2).
- NeMo Agent Toolkit (Fase 2).
- Reservas reales, integración con iHotelier, integración con Zoho (Fase 3).
- Shadow DOM / integración con el sitio en producción / cambios de CSP (Fase 3-4).
- Docker, elección de proveedor de hosting (Fase 4).
- Memoria persistente entre sesiones, analytics (post-MVP).
