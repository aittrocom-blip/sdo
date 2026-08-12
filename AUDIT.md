# AUDIT.md — Sol de Oro AI Concierge · Fase 0

**Alcance:** auditoría del sitio actual (HTML/CSS/JS) y de Supabase. No se modificó nada del sitio ni de la base de datos para este documento — todos los hallazgos vienen de lectura directa de archivos y de queries `SELECT` de solo lectura.

**Fecha:** 2026-08-12

---

## 1. Resumen ejecutivo

El sitio de Sol de Oro es un conjunto de **16 páginas HTML estáticas** (sin build step, sin framework, sin bundler) servidas desde hosting compartido (Hostinger, vía `.htaccess`), con **Supabase** como backend ligero para el contenido que cambia seguido (imágenes, ofertas, gastronomía, cultura). Hay un panel admin (`admin/index.html`) que ya es, en la práctica, un mini-CMS: login con Supabase Auth, CRUD sobre 5 tablas.

**El hallazgo más importante para este proyecto:** gran parte de la información que el Concierge necesitaría responder — los 9 tipos de habitación con specs completas, las 8 salas de eventos con capacidad/m²/piso, el FAQ completo de políticas, los platos del restaurante — **ya existe, está bien escrita, pero vive hardcodeada en HTML**, no en Supabase. Nada de esto está duplicado en la base de datos. Antes de escribir un solo agente, ese contenido necesita un hogar estructurado — si no, el Concierge no tiene de dónde leer "necesito un salón para 80 personas" o "¿tienen jacuzzi?".

Segundo hallazgo importante: **el CSP actual del sitio bloqueará el widget tal como está especificado.** Cada página tiene `script-src 'self'` y `connect-src 'self'` (sin el dominio del Concierge). Esto no es un problema de arquitectura del Concierge — es una línea de configuración que hay que decidir y aplicar en 13 páginas + `.htaccess` + `_headers` antes de que el widget cargue o pueda hacer `fetch()`.

---

## 2. Arquitectura actual del sitio

```text
soldeoro (Hostinger, hosting compartido — Apache)
│
├── *.html (16 páginas, sin build, sin framework)
├── assets/
│   ├── styles.css   (~2270 líneas, un solo archivo, todo el sitio)
│   ├── scripts.js   (~280 líneas, vanilla JS, todo el sitio)
│   └── images.json  (manifiesto editable desde editor-imagenes.html)
├── admin/
│   └── index.html   (mini-CMS: login Supabase Auth + CRUD)
├── images/           (fotos propias del hotel, por categoría)
├── .htaccess         (headers de seguridad, CSP a nivel servidor)
└── _headers          (headers estilo Netlify/CF Pages — probablemente inerte en Hostinger)
```

**Puntos clave:**

- **Sin Node/Python en el hosting actual.** Es hosting de archivos estáticos vía Apache. Cualquier backend (FastAPI, NeMo Agent Toolkit, etc.) **tiene que vivir en otra infraestructura** — no puede desplegarse en el mismo hosting que sirve el HTML. Esto ya está contemplado en el blueprint (Fase 4), solo lo confirmo con evidencia concreta.
- **Cada página repite su propio `<meta http-equiv="Content-Security-Policy">`**, y además `.htaccess` fija un CSP a nivel de header HTTP real (más fuerte que el meta tag). Son dos fuentes de verdad que hoy están sincronizadas pero no vinculadas — cualquier cambio de CSP hay que aplicarlo en ambos lugares.
- **Un solo stylesheet global** (`assets/styles.css`) define los design tokens de todo el sitio:
  ```css
  --black:#171717; --ink:#262626; --gray:#6F6B65; --muted:#9E9A93;
  --sand:#C8B89C; --sand-deep:#9C8A6F; --cream:#F8F6F2; --soft:#F2F0EB;
  --line:#E6E2DA; --white:#FFFFFF;
  ```
  Tipografía: **Roboto** (300/400/500/700) vía Google Fonts, es la única familia en todo el sitio — no hay una fuente serif/display separada.
- **`experiencias.html` tiene su propio sub-tema** (`--cw-*`) con el mismo dorado de marca que usa el panel admin: `--cw-gold: #b38b3a` (idéntico a `--gold` del admin). Esa página también es la única que usa Leaflet (vía unpkg/jsdelivr + tiles de OpenStreetMap/CartoDB) para un mapa interactivo — sin API key, gratis. `ubicacion.html` en cambio usa un iframe de Google Maps embed (también gratis, sin API key, vía `cid=`).
- **Motor de reservas:** iHotelier (`https://soldeoro.ihotelier.com/es/book/dates-of-stay`), externo, ya integrado como link directo. No hay API propia de reservas ni PMS conectado.
- **Formulario de cotización de eventos (`eventos.html`) NO está conectado a nada real todavía** — es `onsubmit="event.preventDefault(); alert(...)"`. Un reporte interno del equipo (`REPORTE_WEB.md`, mayo 2026) dice que los campos están "listos para apuntar al webhook de Zoho", pero el webhook no está cableado. Esto es relevante: el conector de Zoho CRM que ya tienes disponible en esta sesión probablemente es para ese mismo pipeline de leads — vale la pena unificar el "Action Agent" del Concierge con ese mismo destino en vez de crear un canal paralelo.

---

## 3. Supabase — inventario completo

Proyecto: `fjzshpilzjtfjcouzzzz`. Confirmé el listado real de tablas vía el endpoint OpenAPI de PostgREST (no asumido, no copiado de código viejo).

### 3.1 Tablas existentes (6, todas en schema `public`)

| Tabla | Filas (aprox.) | Uso actual | RLS |
|---|---|---|---|
| `le_restaurants` | 8 | Carrusel "Gastronomía" en `experiencias.html` | público SELECT · `authenticated` ALL |
| `le_cultural` | 8 | Carrusel "Cultura" en `experiencias.html` | público SELECT · `authenticated` ALL |
| `le_experiences` | ~40 | **No se usa en ninguna página pública.** Solo existe en el admin (tab "Experiencias"). El contenido real de "Explorar Lima" en `experiencias.html` está hardcodeado en HTML, no lee esta tabla. | público SELECT · `authenticated` ALL |
| `offers` | variable | Página `ofertas.html` | público SELECT · `authenticated` ALL |
| `site_images` | ~60+ | Imágenes editables por página/sección, usado en `index`, `habitaciones`, `restaurante`, `eventos`, `servicios`, `ofertas` vía `data-img` + `assets/scripts.js` | público SELECT · `authenticated` ALL |
| `site_content` | 64 | **Existe y tiene datos reales (textos de hero, nombres de 9 habitaciones, nombres de 7 salones, 5 platos), pero no tiene UI en el admin.** Nadie la edita desde el panel hoy — hay que ir directo a SQL/API para tocarla. | público SELECT · `authenticated` ALL |

**Nota sobre RLS:** el patrón es siempre el mismo — lectura pública total, escritura total para *cualquier* usuario autenticado (`auth.role() = 'authenticated'`), sin distinción de rol/claim. Con un solo usuario admin esto no es un problema hoy, pero si el Concierge algún día necesita escribir en Supabase (p. ej. guardar analytics, leads), conviene usar una política separada en vez de heredar el mismo "cualquier autenticado puede todo".

### 3.2 Storage

- Bucket `experiences` (público) — ya en uso, contiene las fotos de restaurantes/cultura/experiencias que subí en esta sesión bajo `restaurants/` y `explore/`.
- **No hay bucket dedicado a analytics/logs/conversaciones.** Si el Concierge necesita persistir algo (Sección 24 del blueprint), habría que crear tabla(s) nuevas — no hay nada reutilizable ahí.

### 3.3 Auth

- Un solo usuario: `aittro.com@gmail.com` (admin del panel). Email/password vía Supabase Auth. No hay roles/claims custom, no hay tabla de "usuarios del hotel" ni de huéspedes.

### 3.4 Lo que NO existe (y el blueprint da por hecho que hay que revisar antes de crear)

Confirmado por inspección directa del schema — **no hay tablas para:** habitaciones/rooms, salones/salons, eventos/reservations, políticas/FAQ, información general del hotel, ubicación/coordenadas estructuradas, contactos, sesiones de conversación, analytics. Todo eso hoy es HTML estático (ver sección 4).

---

## 4. Dónde vive hoy cada dominio de información (mapa completo)

Esto es lo más importante del audit: para cada dominio que el Concierge necesita cubrir (Sección 33 del blueprint), esto es *exactamente* dónde está la fuente de verdad hoy, y si está en HTML o en Supabase.

| Dominio | Fuente real hoy | ¿Dónde? | ¿Estructurado? |
|---|---|---|---|
| **Habitaciones** (9 tipos, m², cama, vista, capacidad, amenidades, foto) | HTML (`data-*` attrs) | `habitaciones.html` líneas ~232-240 | Sí, pero en atributos HTML, no en BD |
| Nombres/precio base de habitaciones | Supabase | `site_content` (page=`habitaciones`) | Parcial — solo nombre, sin specs |
| **Salones/eventos** (8 salas, capacidad, m², piso, tipo de montaje) | HTML (`<table>`) | `eventos.html` línea ~374, tabla `#capacidad` | Sí, tabla HTML real, muy completa |
| Nombres de salones | Supabase | `site_content` (page=`eventos`) | Parcial — solo nombre |
| **Restaurante** (platos, horarios) | HTML + Supabase (parcial) | `restaurante.html` + `site_content` (page=`restaurante`) | Parcial |
| **Políticas / FAQ** (check-in/out, mascotas, tarjetas, cancelación, voltaje, moneda, idiomas) | HTML (`<details>/<summary>`) | `faq.html`, ~30 preguntas ya redactadas en tono hospitalario | Sí, pero sin IDs ni estructura de datos |
| **Gastronomía cercana** (6 restaurantes + Malecón) | Supabase | `le_restaurants` | Sí ✅ |
| **Cultura cercana** | Supabase | `le_cultural` | Sí ✅ |
| **Explorar Lima** (19 tarjetas: hotel, compras, costa, paseos, empresarial) | HTML puro | `experiencias.html`, sección `#locScatter` | Sí, pero en HTML, no en BD |
| **Ubicación / distancias / GPS** | HTML | `ubicacion.html` (coords: `-12.1207, -77.0338`, dirección `Calle San Martín 305, Miraflores`) | No — texto libre, sin lat/lng reutilizable salvo ese único punto |
| **Contacto** (teléfonos, emails, WhatsApp) | HTML (footer, repetido en cada página) | Recepción `+51 (1) 610-7000`, Reservas `+51 988 861 380` / `reservas@soldeoro.pe`, Eventos `comercial@soldeoro.pe`, WhatsApp `wa.link/dc0dft` | No |
| **Reservar habitación** | Link externo | iHotelier (`soldeoro.ihotelier.com`) | N/A — ya es una acción, no dato |
| **Cotizar evento** | Formulario roto | `eventos.html`, no conectado a nada | N/A |
| **Ofertas** | Supabase | `offers` | Sí ✅ |
| **Servicios/amenidades del hotel** (piscina, gimnasio, spa, wifi, etc.) | HTML + Supabase (fotos) | `servicios.html` + `site_images` (page=`servicios`) — ya reutilizado para la sección "En el Hotel" que agregamos hoy | Parcial |

---

## 5. Elementos reutilizables (no reinventar)

- **Paleta e identidad visual:** `--gold: #b38b3a` es el dorado de marca, ya consistente entre el admin, `experiencias.html` y el ícono/isotipo que agregamos al sidebar admin (`assets/sol-de-oro-icon.png`, recortado del logo oficial). El widget del Concierge debería heredar este dorado + la paleta cálida (`--cream`, `--sand`) para sentirse nativo, tal como pide la Sección 14 del blueprint.
- **Tipografía:** Roboto 300/400/500/700 — no introducir una fuente nueva para el widget.
- **Patrón de "acción" ya existente en el sitio:** CTAs duales tipo `[Reservar] [Consultar disponibilidad]` (habitaciones), `[Ver salones] [Cotizar]` (eventos), `[Cómo llegar] [Ver experiencia]` (loc-cards) — el formato `actions: [...]` del blueprint (Sección 16) calza naturalmente con un patrón que el sitio ya usa visualmente. Reusar los mismos labels donde aplique, no inventar nuevos.
- **Mapas sin costo:** el sitio ya resuelve "cómo llegar" con Google Maps embed gratuito (iframe `cid=`) y con Leaflet+OSM. El Concierge puede seguir el mismo patrón para el CTA `MAP` sin pagar Google Maps API — cada `maps_url` en `le_restaurants`/`le_cultural` ya es un link `maps.google.com/?q=...` listo para usar tal cual.
- **Patrón admin ya construido:** el CRUD del panel (`admin/index.html`) es un ejemplo funcionando de "Supabase + auth + edición en vivo" — si el Concierge necesita un panel de analytics o de gestión de knowledge base, ese mismo patrón (una sola página HTML, sin framework, auth con Supabase) es consistente con "no convertir a React".
- **`site_content` como tabla clave-valor genérica** ya existe y ya cubre parte de "hotel_information" — antes de crear una tabla nueva de `hotel_information`, evaluar extender esta.

---

## 6. Problemas encontrados (independientes del proyecto del Concierge, pero relevantes)

1. **CSP bloqueará el widget tal cual está.** `script-src 'self'` y `connect-src 'self'` en las 13 páginas + `.htaccess`. Sin actualizar esto, ni el `<script src="https://CONCIERGE_DOMAIN/widget.js">` cargará, ni sus `fetch()` a `/api/concierge` funcionarán. Hay que decidir el dominio del Concierge *antes* de tocar el CSP, y aplicarlo en 3 lugares (meta tags × 13 páginas, `.htaccess`, `_headers`).
2. **El formulario de cotización de eventos no envía nada a ningún lado.** Si el Action Agent del Concierge va a generar leads de eventos, hoy no hay ningún backend real esperándolos del lado del sitio — tendría que ser el propio backend del Concierge el que reciba y enrute esos leads (a Zoho, a email, o a ambos).
3. **`le_experiences` está huérfana.** Tiene ~40 filas cargadas pero ninguna página pública la lee. Si se usa como fuente para el Concierge, hay que decidir si also se conecta a una página pública o si queda solo como fuente de datos para el agente (uso legítimo, pero vale la pena que lo sepas).
4. **RLS "todo o nada" para escritura.** Cualquier usuario autenticado tiene `ALL` en todas las tablas. Bien para un panel admin de una sola persona; no ideal si el Concierge backend también termina autenticándose contra el mismo proyecto — mejor usar la `service_role` key desde el backend (nunca expuesta al frontend, tal como pide la Sección 21) en vez de crear un usuario "concierge" con rol authenticated.
5. **Sin schema para conversaciones/analytics/sesiones.** Si se implementa la Sección 24 (analytics anónimos) o memoria de sesión server-side, hay que crear tablas nuevas — no hay nada que reutilizar.

---

## 7. Información faltante para que el Concierge cumpla el criterio de éxito (Sección 33)

Cruzando la lista de preguntas objetivo del blueprint contra lo que existe hoy:

| Pregunta de ejemplo | ¿Se puede responder hoy con datos estructurados? |
|---|---|
| ¿Dónde está el hotel? | ✅ (`ubicacion.html`, texto + 1 coordenada) |
| ¿Qué habitaciones tienen? | ⚠️ Datos completos pero en HTML, no en BD |
| ¿Qué servicios ofrecen? | ⚠️ Parcial (HTML + `site_images`) |
| ¿Qué instalaciones tienen? | ⚠️ Igual que arriba |
| ¿Qué puedo hacer cerca / caminando / en Miraflores? | ✅ (recién estructurado hoy: `le_restaurants`, `le_cultural`; ⚠️ "Explorar Lima" sigue en HTML) |
| ¿Qué museos hay cerca? / ¿Qué es Huaca Pucllana? | ✅ (`le_cultural`) |
| ¿Dónde puedo comprar souvenirs? / ¿Dónde está Larcomar? | ⚠️ En HTML (`experiencias.html`), no en BD |
| ¿Qué salones tienen? / salón para 80 personas | ❌ Tabla de capacidades completísima pero 100% en HTML, no consultable por un agente sin parsearla |
| Quiero reservar una habitación | ✅ (link directo a iHotelier, ya es una acción) |
| Quiero cotizar un evento | ❌ Formulario no funcional, sin backend receptor |

**Conclusión:** el gap no es de contenido — el contenido casi todo *existe* y está bien escrito. El gap es que vive en HTML donde un agente no lo puede consultar de forma confiable ni acotada. La prioridad #1 antes de programar agentes es **migrar (no reescribir) ese contenido a Supabase**, reusando el texto ya redactado.

---

## 8. Propuesta concreta

### 8.1 Tablas nuevas a crear (mínimas, sin duplicar lo que ya existe)

Siguiendo la Sección 9 ("no duplicar si ya existe") y la 32 ("no sobreingeniería"):

```text
rooms              -- migrar desde habitaciones.html (9 filas, ya redactadas)
salons             -- migrar desde eventos.html tabla #capacidad (8 filas, ya redactadas)
hotel_faq          -- migrar desde faq.html (~30 preguntas, ya redactadas, agrupadas por sección)
hotel_info         -- opcional: evaluar extender site_content en vez de tabla nueva
```

**NO crear:** tabla nueva de "experiences" (ya existe `le_experiences`, solo falta decidir si el Concierge la usa tal cual o si primero se sincroniza con lo que hay en `experiencias.html`), ni tabla de "restaurants cercanos" (ya existe `le_restaurants`), ni tabla de "cultural places" (ya existe `le_cultural`).

**Decisión pendiente que necesito de ustedes:** ¿migro también el contenido de "Explorar Lima" (19 tarjetas hoy en HTML) a `le_experiences` — que ya existe pero está huérfana — para que sirva doble propósito (fuente del Concierge + eventualmente reconectar la página pública a la BD)? Es el camino más consistente con "no duplicar", pero implica re-trabajar esa sección otra vez tan pronto la acabamos de dejar bien.

### 8.2 Sobre NeMo Agent Toolkit (Sección 5 del blueprint)

Lo uso si es la decisión ya tomada, pero una observación honesta antes de comprometerse: NeMo Agent Toolkit está pensado para orquestación de agentes a escala NVIDIA/NIM, con más superficie (tracing, evals, profiling multi-agente) de la que un MVP de 3 agentes + 1 router realmente necesita. Con los ~15 intents de la Sección 8 y 3 agentes de contenido, un router simple en FastAPI (function-calling / clasificación con un modelo pequeño) cubre el mismo flujo con menos piezas móviles y menos fricción para correr en free tier. Dicho eso, si NeMo Agent Toolkit ya es un requisito de negocio (no técnico) — por ejemplo, alineamiento con NVIDIA como partner — lo respeto y lo uso; solo lo señalo porque la Sección 32 del propio blueprint pide evitar sobreingeniería y quiero que la decisión sea informada, no que la tome yo por mi cuenta.

### 8.3 Sobre el CSP

Antes de la Fase 1, van a necesitar decidir el dominio del Concierge (aunque sea provisional) para poder:
1. Agregarlo a `script-src` y `connect-src` en las 13 páginas + `.htaccess` + `_headers`.
2. Considerar centralizar el CSP (hoy está triplicado) para que el próximo cambio no requiera tocar 15 archivos.

### 8.4 Integración con Zoho

Ya hay un conector de Zoho CRM disponible en este entorno. Dado que el formulario de eventos "iba a apuntar a Zoho" según el reporte interno, sugiero que el **Action Agent** (Sección 7) escriba leads de reservas/cotizaciones directo a Zoho en vez de (o además de) email/WhatsApp — unifica el pipeline comercial que ya está planeado, en vez de crear un canal nuevo que el equipo comercial no revisa.

---

## 9. Lo que NO toqué

Ni el HTML del sitio, ni `assets/styles.css`, ni `assets/scripts.js`, ni ninguna tabla de Supabase. Todas las queries de esta auditoría fueron `SELECT`. El único archivo nuevo es este `AUDIT.md`.

---

## 10. Próximo paso

Esperando autorización, como pide la Sección 27. Cuando la tengan, mi recomendación de orden es:

1. Decidir dominio del Concierge (aunque sea de staging) → desbloquea el CSP.
2. Decidir si migro "Explorar Lima" a `le_experiences` o la dejo en HTML.
3. Crear `rooms`, `salons`, `hotel_faq` en Supabase migrando el contenido ya redactado (sin inventar texto nuevo).
4. Recién ahí, Fase 1 del blueprint: UI + `/api/concierge` + router de intención + lectura de Supabase, sin agentes todavía, sin reservas reales.
