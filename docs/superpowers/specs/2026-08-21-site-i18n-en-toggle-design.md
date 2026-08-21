# Sitio en inglés — infraestructura de traducción (Sub-proyecto A)

**Fecha:** 2026-08-21
**Estado:** Aprobado por el usuario, listo para plan de implementación.

## Contexto y alcance de este documento

El usuario pidió que el sitio de Sol de Oro tenga una versión completa en inglés, activable
desde el selector `ES / EN` que ya existe (solo visual, sin funcionalidad) arriba a la derecha
del header, en las 14 páginas del sitio, e incluyendo la conversación del AI Concierge.

Este pedido se descompuso en 3 sub-proyectos independientes, cada uno con su propio ciclo de
spec → plan → implementación:

- **(A) — este documento**: infraestructura de traducción del sitio (el toggle ES/EN
  funcional + las 14 páginas traducidas al inglés). Es la base técnica de la que dependen
  los otros dos.
- **(B) — futuro, depende de A**: idioma del Concierge de IA. El saludo inicial y los
  textos fijos del widget (placeholder, botón Enviar, saludos de bienvenida) siguen el
  idioma de la página (vía `window.getSiteLang()`, expuesto por este sub-proyecto A). La
  conversación ya en curso sigue reaccionando al idioma en que escribe el huésped (regla
  existente en el system prompt, sin cambios). El mensaje de derivación por WhatsApp y los
  datos guardados en Supabase/Zoho quedan en el idioma real de la conversación, no
  necesariamente en el idioma de la página.
- **(C) — futuro, independiente técnicamente pero necesario para la calidad de (B)**:
  contenido real en inglés en las tablas de Supabase que usa el Concierge (habitaciones,
  FAQ, ofertas, lugares cercanos, restaurantes, cultura, salones), para que las respuestas
  en inglés se basen en datos reales y no en una traducción improvisada por el modelo —
  misma regla de "nunca inventes, usa el dato literal de la herramienta" que ya rige hoy.

Este documento cubre **solo (A)**.

## Objetivo

Que cualquiera de las 14 páginas estáticas del sitio pueda mostrarse completamente en
inglés al activar "EN" en el selector de idioma del header, sin recargar la página, y que
esa elección persista mientras el visitante navega por el resto del sitio.

## Por qué este enfoque

El sitio no tiene build step ni sistema de templates — las 14 páginas HTML se editan a
mano y comparten `assets/scripts.js`/`assets/styles.css` como únicos archivos comunes
(confirmado en el trabajo de este mismo proyecto: el bloque CSP de la Fase 1 y las
etiquetas del widget del Concierge estaban duplicados literalmente en cada uno de los 14
archivos). Cualquier solución de traducción tiene que funcionar dentro de esa realidad, sin
introducir un paso de compilación.

Se evaluaron dos enfoques:

1. **Diccionario de traducciones + atributos `data-i18n`** (elegido): cada elemento
   traducible lleva `data-i18n="clave"`; un archivo separado mapea claves a texto en
   inglés; un script recorre la página y hace el swap. Los archivos HTML no crecen (un
   solo idioma visible en el markup), y se puede verificar programáticamente que ninguna
   clave quede sin traducir.
2. **Ambos idiomas inline en el mismo HTML** (descartado): cada texto va dos veces en el
   archivo, mostrando uno u otro según el idioma activo vía CSS/JS. Más simple de
   inspeccionar a simple vista, pero prácticamente duplica el tamaño de archivos que ya
   superan las 1000 líneas (habitaciones.html, experiencias.html), y no permite un chequeo
   automático de cobertura tan directo.

## Arquitectura

### 1. Diccionario de traducciones

Un único archivo `assets/i18n/en.js` que define `window.I18N_EN = { "clave": "texto en
inglés", ... }`, cargado con un `<script>` normal (sin módulos, sin bundler) en las 14
páginas, igual que `assets/scripts.js` y `assets/styles.css` hoy. Un solo archivo combinado
para las 14 páginas — más simple de mantener que 14 diccionarios sueltos, y el costo de
tamaño de archivo (texto plano) es irrelevante para un sitio de este tipo.

### 2. Marcado de contenido traducible

- **Texto de un elemento**: `data-i18n="clave"` → el script reemplaza `textContent` (o
  `innerHTML` cuando el nodo contiene markup interno, ej. un `<strong>` dentro de un
  párrafo — a decidir caso por caso durante la implementación, prefiriendo `textContent`
  siempre que sea posible).
- **Atributos** (placeholder, `alt`, `aria-label`, `title`): `data-i18n-attr` con el
  formato `"atributo:clave"`, admitiendo varios separados por coma (ej.
  `data-i18n-attr="placeholder:common.reserve.promo_placeholder"`).

### 3. Nomenclatura de claves

- **`common.*`** — todo lo que se repite igual en las 14 páginas: navegación y
  mega-menús del header, footer completo, la barra de reserva (incluyendo el panel de
  huéspedes con steppers agregado recientemente), y cualquier otro fragmento compartido.
  Se traduce una sola vez en el diccionario y aplica a las 14 páginas.
- **`<página>.<slug>`** — contenido específico de una página, con el nombre base del
  archivo como prefijo (ej. `index.hero.title`, `habitaciones.showcase.intro`,
  `faq.q1.answer`).

### 4. Alcance del contenido a traducir

Todo texto visible al huésped: títulos, párrafos, botones, labels, atributos `alt` de
imágenes relevantes, y las `<meta name="description">` de cada página (para SEO en
inglés). No se traducen nombres propios (Sol de Oro, Miraflores, Restaurante Murano) ni
datos de contacto (teléfonos, emails, direcciones).

### 5. Mecanismo de activación (nuevo bloque en `assets/scripts.js`)

- Al cargar la página: lee `localStorage.getItem('site_lang')` (default `'es'` si no
  existe o si `localStorage` no está disponible — envuelto en `try/catch`, nunca rompe la
  carga de la página). Si es `'en'`, aplica las traducciones inmediatamente y setea
  `<html lang="en">`.
- El selector `ES / EN` del header (hoy un `<span>` sin interacción) pasa a ser dos
  elementos clicables (ej. `<button class="lang-btn" data-lang="es">` /
  `data-lang="en">`). Al hacer clic: aplica las traducciones correspondientes (sin
  recargar la página), persiste la elección en `localStorage`, actualiza `<html lang>`, y
  refleja el estado activo visualmente (mismo patrón que ya usa `.tab.active` en la barra
  de reserva).
- Esta lógica va en el `<span class="lang">` del header Y en su duplicado del menú móvil
  (`mobile-nav-footer`), ya visto en el trabajo de Fase 3 de este proyecto.
- **Clave faltante**: si una `data-i18n` no tiene entrada en `I18N_EN`, se deja el texto
  en español tal cual (nunca queda vacío/undefined) y se registra un `console.warn` — no
  interrumpe la navegación del huésped.

### 6. Interfaz para consumidores futuros (sub-proyecto B)

Se expone `window.getSiteLang()`, una función mínima que devuelve `'es'` o `'en'` leyendo
la misma clave de `localStorage`. El widget del Concierge (sub-proyecto B, fuera de este
documento) la usará para decidir el idioma de su saludo inicial y textos fijos, sin
duplicar la lógica de lectura de `localStorage`.

## Testing / verificación

No hay suite de tests automatizados para este frontend (confirmado en trabajo previo de
este mismo proyecto — sitio estático sin tooling de test). La verificación es:

1. **Playwright contra un servidor local**: togglear ES/EN en varias páginas, confirmar
   que el texto visible cambia, que la elección persiste al navegar a otra página
   (recargando/visitando una segunda URL), y que vuelve a español al togglear de nuevo.
2. **Chequeo estático de cobertura** (script de verificación, no parte del sitio en sí):
   recorre las 14 páginas, junta todas las claves `data-i18n`/`data-i18n-attr` realmente
   usadas en el HTML, y las cruza contra las claves definidas en `assets/i18n/en.js` —
   reporta cualquier clave usada sin traducción definida, y cualquier clave definida que
   ya no se use en ningún HTML (diccionario con basura acumulada).

## Volumen de trabajo y forma de ejecución

Traducir las 14 páginas completas implica varios cientos de strings de contenido. El plan
de implementación (siguiente paso, vía la skill `writing-plans`) probablemente reparta
este trabajo en tareas por página o por bloque de páginas, ejecutadas en paralelo por
sub-agentes — mismo patrón usado para propagar el panel de huéspedes de la barra de
reserva a las 11 páginas que la usan, pero a mayor escala (14 páginas, mucho más
contenido por página).

## Fuera de alcance de este documento

- Idioma del Concierge de IA (sub-proyecto B).
- Contenido en inglés en Supabase (sub-proyecto C).
- Traducción a idiomas distintos de inglés.
- Detección automática de idioma del navegador (`Accept-Language` / `navigator.language`)
  como default inicial — el default es siempre español hasta que el visitante togglee a
  EN, salvo que el usuario pida lo contrario más adelante.
