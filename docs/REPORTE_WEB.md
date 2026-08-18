<div align="center">
  <img src="aittro-logo.png" alt="Aittro" width="180" />
</div>

# Reporte de avance · Nueva Web Sol de Oro

**Para:** Gerencia General · Sol de Oro Hotel &amp; Suites
**De:** Aittro · Equipo de Proyecto Web
**Fecha:** Mayo 2026
**Asunto:** Refocus estratégico de la presencia digital, captura unificada de requerimientos vía Zoho y avances de implementación.

---

## 1. Resumen ejecutivo

Estamos rediseñando soldeoro.com.pe con un objetivo comercial claro: **convertir más cotizaciones de eventos** (línea de mayor margen y volumen), sosteniendo en paralelo la captura directa de hospedaje y la visibilidad del Restaurante Murano. La nueva web está pensada también como un canal centralizado de **captura de requerimientos de clientes** desde la página y desde redes sociales, todos consolidados en Zoho para el equipo comercial.

**Tres ejes del rediseño:**

1. **Eventos & Salones como protagonista comercial** — flujo completo desde el primer click hasta el lead cualificado en Zoho.
2. **Hospedaje y Restaurante como complementarios** — diseñados para sostener marca, autoridad y experiencia premium, integrados con motor iHotelier y reservas Murano.
3. **UX consistente, premium y medible** — sistema de diseño editorial unificado, navbar adaptativa, barra de reserva siempre visible, contenido organizado en páginas dedicadas con narrativa propia.

---

## 2. Diagnóstico de la web actual (soldeoro.com.pe)

Luego de auditar las 8 secciones públicas, detectamos las siguientes brechas críticas para el negocio:

### 2.1 Gaps comerciales

| Brecha | Impacto |
|---|---|
| Eventos tratado como una sección informativa más, sin diferenciación visual ni funnel | Pérdida de leads B2B (bodas, corporativos, convenciones) |
| Una sola CTA por página (mailto), sin formulario de cotización ni captación de datos | 0% de leads estructurados, todo manual |
| Sin integración con CRM | Imposible medir ROI por canal o etapa del funnel |
| Sin precios publicados (habitaciones, eventos, restaurante) | Fricción de entrada, todo depende de iHotelier o contacto manual |
| No hay carta del restaurante ni embed de menú | Murano queda como mención, no como destino |
| Reservas dependen 100% del motor iHotelier externo (sin overlay propio) | La web no aporta valor comercial al embudo |

### 2.2 Gaps de UX y contenido

- Página `/contacto/`, `/como-llegar/`, `/libro-de-reclamaciones/`, `/politica-de-privacidad/`, `/terminos-y-condiciones/` → **devuelven 404** (riesgo legal en Perú).
- Datos inconsistentes: aforo total dice "1,000 personas" en home y "980" en eventos. Distancias a Larcomar y Parque Kennedy difieren entre home y `/ubicacion/`.
- Suite Deluxe: ficha dice "1 cama King" y descripción dice "dos camas queen".
- Email del hotel: `@soldeoro.pe` mientras dominio web es `.com.pe`.
- Galería sin captions, sin SEO descriptive, sin filtros funcionales.
- Blog con sólo 2 posts, ambos sin categoría asignada.
- Sin versión en inglés (esperable para un cinco estrellas en Miraflores).
- Wyndham Rewards no aparece en la web actual a pesar de afiliación histórica.

---

## 3. Refocus estratégico de la nueva web

### 3.1 Eventos & Salones — protagonista comercial

**Objetivo:** convertir cada visita interesada en evento en un lead cualificado dentro de Zoho CRM en menos de 2 minutos.

**Implementado:**

- **Página dedicada `eventos.html`** con hero editorial, mosaico visual de los 6 salones, tabla de capacidades por configuración (banquete · cocktail · auditorio · aula · forma U · área), grilla de tipos de evento (bodas, conferencias, reuniones ejecutivas, convenciones, quinceañeros, lanzamientos), y formulario de cotización.
- **Reservation bar persistente** en todas las páginas con tab "Salones" pre-seleccionado al ingresar a `eventos.html` — el GM no necesita explicar dónde cotizar, está siempre visible.
- **Mega menú** "Salones" en el header con preview visual de los tres salones insignia y CTA directo a cotización.
- **Formulario estructurado** con campos clave para calificar el lead (tipo de evento, fecha tentativa, número de asistentes, contacto). Los campos están listos para apuntar al webhook de Zoho.
- **Stats bar** de credibilidad: 1.000 invitados máximo · 6 salones modulares · 30+ años organizando · 24h respuesta.

### 3.2 Hospedaje — sostén de marca, conversión vía iHotelier

**Implementado:**

- **Showcase interactivo** de 9 categorías (Standard hasta Grand Deluxe Suite) con imagen grande clickeable, specs (m², cama, vista, capacidad), lista de amenidades, CTAs duales "Reservar esta habitación" + "Consultar disponibilidad".
- **Page hero** con imagen real de la habitación, lead que destaca el ADN del hotel.
- **Reservation bar tab "Hospedaje" pre-activada** en `habitaciones.html`.
- Estructura preparada para conectar a iHotelier vía URL parametrizada (categoría preseleccionada).

### 3.3 Restaurante Murano — complementario, generador de tráfico local

**Implementado:**

- Página `restaurante.html` con hero del plato signature, **quote del chef**, **4 momentos del día** (desayuno · almuerzo · cena · bar) con horarios precisos.
- Tira de **6 platos signature** que invitan al comensal externo, no sólo al huésped.
- Reservation bar tab "Restaurante" pre-activada con campos específicos (fecha, hora, comensales, ocasión).
- Diferenciación clara entre "comensal externo" y "huésped" en el copy.

### 3.4 Marca y experiencia transversal

- **Navbar adaptativa por contraste**: transparente sobre imágenes oscuras (hero, page-hero, award-band, footer), blanca sobre contenido claro. La marca siempre legible, sin perderse.
- **Sistema de diseño editorial**: paleta sand/cream/ink, tipografía Roboto, jerarquía con eyebrows + h2 + lead.
- **Animaciones de entrada** (reveal + scatter polaroid en Ubicación) para sensación premium sin sacrificar performance.
- **Galería filtrable** por habitaciones / espacios / gastronomía / eventos — uso comercial directo (presentación a wedding planners, agencias).

---

## 4. Avances logrados a la fecha

### 4.1 Estructura del sitio

| Página | Estado | Función comercial |
|---|---|---|
| `index.html` (home) | ✅ Listo | Landing editorial + reservation bar |
| `habitaciones.html` | ✅ Listo | Showcase + integración iHotelier |
| `eventos.html` | ✅ Listo | **Funnel de leads B2B** |
| `restaurante.html` | ✅ Listo | Reservas mesa + posicionamiento Murano |
| `servicios.html` | ✅ Listo | Justifica la categoría 5★ |
| `galeria.html` | ✅ Listo | Material visual filtrable |
| `ubicacion.html` | ✅ Listo | Mapa Google + 16 lugares + transporte |
| `ofertas.html` | ✅ Listo | Promociones con códigos |
| `acerca.html` | ✅ Listo | Historia, equipo, certificaciones |

### 4.2 Componentes clave operativos

- Reservation bar tri-modal (Hospedaje · Salones · Restaurante) anclada al pie de pantalla.
- Mega menús con preview visual.
- Formulario de cotización de eventos con campos para CRM.
- Embed de Google Maps tinted al estilo de la marca en `ubicacion.html`.
- Footer unificado con isotipo, redes sociales, datos de contacto y links a todas las secciones.

### 4.3 Decisiones de diseño aplicadas

- Paginación independiente por tema (vs single-page) → mejor SEO, mejor tracking, mejor experiencia compartida.
- Home "teaser" minimalista: cada sección tiene un avance breve con CTA "Ver todo" hacia la página dedicada.
- Sección Ubicación edge-to-edge con grid 6×2 de lugares recomendados — diferenciación visual única.

---

## 5. Comparativa UX · Web actual vs Nueva web

| Dimensión | Web actual (soldeoro.com.pe) | Nueva web |
|---|---|---|
| **Eventos** | Una sección informativa, 1 CTA email | Página dedicada con funnel completo, formulario CRM-ready |
| **Reservas** | Botón "Reservar" → sale del sitio a iHotelier | Reservation bar siempre visible, 3 modos, lleva a iHotelier con contexto |
| **Restaurante** | Página con horarios, sin carta | Página editorial con momentos del día, platos signature, reserva integrada |
| **Habitaciones** | 9 cards estáticas con descripción | Showcase interactivo, swap por click, specs detalladas |
| **Galería** | Filtros que no funcionan, sin captions | Masonry filtrable con captions y categorías |
| **Ubicación** | Texto + lista de distancias | Mapa Google embebido + 16 lugares + transporte detallado |
| **Mobile** | Diseño antiguo, no optimizado | Responsive nativo en todos los breakpoints |
| **Navegación** | Header estático básico | Navbar adaptativa al contraste, mega menús con preview |
| **Performance** | Sin optimización visible | Lazy-loading, CSS extraído, JS modular |
| **Marca** | Logo aplicado sin sistema | Sistema visual cohesivo, isotipo en footer, paleta consistente |
| **Captura de consultas** | Mails dispersos, IG y FB sin centralizar | Formularios y mensajes consolidados en Zoho |

---

## 6. Contenido y narrativa

### 6.1 Lo que la web actual no comunica (y la nueva sí)

- **Por qué Sol de Oro y no otro 5★ en Miraflores**: 30+ años, equipo de 180 personas, cocina de autor abierta al público, salones modulares hasta 1.000 invitados.
- **Diferencial geográfico**: caminable a Maido (#1 Latam según 50 Best), 4 min al Parque Kennedy, 8 min al Malecón, 15 min a San Isidro.
- **Profundidad de oferta de eventos**: bodas, conferencias, directorios, convenciones, lanzamientos, quinceañeros — cada uno con su tratamiento.
- **Capacidades reales por salón**: tabla con 6 configuraciones distintas y áreas en m². El comprador B2B ve lo que necesita sin tener que pedir.
- **Profesionalización del Restaurante**: tres momentos al día, no sólo "buffet".

### 6.2 Pendientes de contenido a coordinar con marketing

- Confirmar capacidades reales de cada salón (la web actual tiene datos contradictorios entre home y página de eventos).
- Carta o link descargable del Restaurante Murano.
- Casos de éxito reales (bodas o corporativos memorables) para landing de eventos.
- Material fotográfico oficial de habitaciones, salones armados, platos del Murano (actualmente usamos imágenes provisorias de Unsplash).
- Política de cancelación, T&C, libro de reclamaciones (obligatorio Indecopi).
- Versión en inglés.

---

## 7. Captura de requerimientos vía Zoho

El alcance de Zoho en este proyecto es **acotado y específico**: ser el punto único donde lleguen todos los requerimientos de clientes — los que entran por la web y los que entran por redes sociales — para que el equipo comercial los gestione sin perder ninguno.

### 7.1 Qué resuelve Zoho aquí

- **Una sola bandeja** para todas las consultas, sin importar el canal de origen.
- **Trazabilidad** de cada requerimiento: fecha, canal, tipo de interés, datos de contacto.
- **Asignación clara** al responsable comercial (eventos / hospedaje / restaurante).
- **Sin pérdida** de mensajes que hoy llegan dispersos a varios correos y a inbox de redes.

### 7.2 Fuentes de entrada de requerimientos

| Origen | Tipo de requerimiento | Llega a Zoho como |
|---|---|---|
| Formulario de cotización (`eventos.html`) | Cotización de salones / eventos | Lead categoría **Eventos** |
| Formulario de reserva de mesa (`restaurante.html`) | Reserva del Restaurante Murano | Lead categoría **Restaurante** |
| Reservation bar — tab Hospedaje | Solicitud de reserva (deriva al motor iHotelier) | Lead categoría **Hospedaje** |
| Mensajes de Instagram | Consultas vía DM | Mensaje en bandeja unificada de Zoho |
| Mensajes de Facebook | Consultas vía Messenger | Mensaje en bandeja unificada de Zoho |
| WhatsApp Business | Consultas vía WhatsApp del hotel | Conversación en Zoho |
| Email a `reservas@` y `comercial@` | Consultas escritas | Ticket en Zoho |

### 7.3 Cómo funciona en la práctica

1. El cliente llena un formulario en la web o escribe por redes / WhatsApp.
2. El requerimiento entra automáticamente a Zoho con su origen identificado (web · IG · FB · WhatsApp · email).
3. Zoho avisa al responsable comercial correspondiente.
4. El equipo responde desde Zoho, dejando el historial completo guardado.

### 7.4 Implementación necesaria

- Conectar los 3 formularios web (eventos, restaurante, hospedaje) al endpoint de Zoho.
- Vincular Instagram y Facebook Messenger del hotel a la bandeja unificada de Zoho.
- Vincular WhatsApp Business a Zoho.
- Configurar reglas simples de asignación: cotización de eventos → comercial; reservas de mesa / hospedaje → recepción.

---

## 8. Próximos pasos

### 8.1 Corto plazo (2–4 semanas)

- Conectar formularios web a Zoho y vincular Instagram, Facebook y WhatsApp al mismo punto de captura.
- Reemplazar imágenes provisorias por material fotográfico oficial.
- Sumar páginas legales: Libro de Reclamaciones, T&C, Política de Privacidad, Cookies.
- Versión EN del sitio (al menos las 4 páginas comerciales: home, habitaciones, eventos, restaurante).
- Carta del Restaurante Murano embebida o descargable.
- Configurar Google Maps real con la ficha del hotel.

### 8.2 Mediano plazo (1–3 meses)

- Casos de éxito en landing de eventos (1 boda, 1 corporativo, 1 social).
- Blog reactivado con contenido estratégico SEO (gastronomía, eventos en Lima, viajes corporativos).
- Live chat / botón WhatsApp persistente en la web.
- Versión PT-BR del sitio.

### 8.3 Largo plazo (3–6 meses)

- Motor de reserva propio sustituyendo iHotelier (sujeto a evaluación).
- Calendario público de disponibilidad de salones.
- Tour virtual 360° de salones y suites.

---

## 9. KPIs propuestos para medir el rediseño

| KPI | Línea base actual | Objetivo 6 meses |
|---|---|---|
| Cotizaciones de eventos / mes | No medible (todo manual) | Capturar y medir, base mes 1 |
| Conversión visita → cotización en `eventos.html` | n/a | ≥ 4% |
| Conversión visita → reserva directa hospedaje | Estimado < 1% | ≥ 3% |
| Tiempo en página `eventos.html` | n/a | ≥ 2 min |
| Click-through reservation bar | n/a | ≥ 8% |
| Reservas de mesa Restaurante | Manual | Trazables, base mes 1 |
| Requerimientos consolidados en Zoho / mes | 0 (dispersos en mails y redes) | ≥ 30 |
| Reseñas Google / TripAdvisor / Booking nuevas | Tendencia actual | +25% |

---

## 10. Cierre

La nueva web no es un rediseño cosmético. Es **una herramienta comercial** que prioriza eventos como protagonista, sostiene la oferta de hospedaje y restaurante, y consolida en Zoho los requerimientos que entran tanto por la web como por redes sociales. Todo lo construido hasta ahora está listo para ser activado comercialmente; lo que falta es el contenido oficial (fotos, carta, casos), las páginas legales, y la conexión técnica de Zoho.

**Recomendación:** validar este reporte con marketing y comercial, confirmar prioridades del próximo sprint y arrancar con la conexión del formulario de eventos a Zoho como primer entregable medible.

---

<div align="center">
  <img src="aittro-logo.png" alt="Aittro" width="120" />
  <br />
  <em>Documento elaborado por <strong>Aittro</strong> · v1 · Mayo 2026</em>
</div>
