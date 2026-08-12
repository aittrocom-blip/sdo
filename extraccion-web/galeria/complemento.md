# Galería — Complemento para la nueva web

> La galería actual tiene 53 imágenes con filtros (Hotel / Habitaciones / Restaurante / Áreas comunes / Eventos) pero algunas están mal etiquetadas. Aquí se propone una organización mejorada y filtros más útiles, basada en lo que **realmente muestran** las imágenes ya descargadas.

---

## Filtros sugeridos para la nueva galería

Más útiles que los 5 actuales:

| Filtro | Justificación |
|---|---|
| Habitaciones | Lo que el huésped más busca antes de reservar |
| Suites y jacuzzi | Up-sell visual: la diferencia justifica el precio |
| Piscina y áreas exteriores | Vende experiencia |
| Spa y gimnasio | Cumple expectativa 5★ |
| Restaurante Murano | Refuerza la propuesta gastronómica |
| Salones de eventos | B2B — montajes distintos |
| Salón Sol de Oro (piso 12) | Diferenciador clave — vista panorámica |
| Fachada y entorno | Localización |

---

## Re-categorización propuesta de las 53 imágenes

> Algunas imágenes están etiquetadas como "Habitaciones" en el sitio actual pero parecen ser eventos o áreas comunes. Esta es la lectura recomendada. ⚠️ Confirmar con cliente antes de aplicar.

### Habitaciones (fotos principales por tipo)
- Standard / Twin / Superior: `FOTOS-WEB-SOL-DE-ORO_11zon-1.jpg`, `FOTOS-WEB-SOL-DE-ORO-1_2_11zon.jpg`, `FOTOS-WEB-SOL-DE-ORO-2_11zon.jpg`, `FOTOS-WEB-SOL-DE-ORO-3_11zon.jpg`
- Suites: `JUNIOR-SUITE_11zon.jpg`, `JUNIOR-SUITE-TWIN_11zon.jpg`, `FOTOS-WEB-SOL-DE-ORO_11zon.jpg` (Executive), `FOTOS-WEB-SOL-DE-ORO-5_11zon.jpg` (Suite Deluxe)
- Grand Deluxe: `FOTOS-WEB-SOL-DE-ORO-3_11zon-2.jpg`

### Piscina y áreas exteriores
- `PISCINA-WEB.webp`, `2_2_11zon.jpg`, `3_3_11zon.jpg`, `9_9_11zon.jpg` (terraza)

### Restaurante
- `8_8_11zon.jpg`, `10_10_11zon.jpg`, `21_21_11zon.jpg`, `23_23_11zon.jpg`, `24_24_11zon.jpg`
- `FOTOS-WEB-SOL-DE-ORO-13/15-2/16` (ambientes)

### Salones de eventos
- Ejecutivos: serie `MG_3999/3965/IMG_3914/8388/8383/3832/3856` + `EJECUTIVO-II-*`
- Empresariales: serie `MG_2145/2211/2212/2226` + `EMPRESARIALES-I/II` + `Empresariales-Aula/Aud-*`

### Salón Sol de Oro (piso 12)
- `MG_2636_edi2-scaled.jpg`, `MG_3383_ED.jpg`, `MG_2588_edi2-scaled.jpg`, `SALA-SOL-DE-ORO-1.jpg`, `IMG_4033_ED.jpg`, `SOL-DE-ORO-MESAS-REDONDAS-1.jpeg`

### Fachada y entorno
- `FACHADA.jpg` (principal), `the-hotel-v13828831_ED.webp`

### Banner / promocional (NO incluir en galería del hotel)
- `PAQUETES-PROMOCIONALES-SDO-22.jpg` — es un banner de marketing, no foto del hotel.

---

## Imágenes faltantes para una galería competitiva (⚠️ producir)

Para que la nueva galería esté a la altura de un 5★, falta material en:

- 🚿 **Baños y duchas** (especialmente de suites con jacuzzi — vende el up-sell)
- 🏋️ **Gimnasio** (en el sitio aparece `4_4_11zon.jpg` etiquetado como "Gimnasio" en `nuestro-hotel`, pero conviene verificar y producir más ángulos)
- 💆 **Spa** (no hay fotos identificables de tratamientos / cabinas)
- 🌃 **Fachada nocturna** (impacto en redes sociales)
- 🌅 **Vista desde habitaciones** y desde la terraza piso 12
- 🍽 **Platos del Restaurante Murano** terminados en buena luz
- 🥂 **Cócteles del Bar Murano**

---

## Sugerencias técnicas para la nueva galería

1. **Lightbox** con navegación por teclado y swipe en mobile.
2. **Lazy loading** — son ~50–60 imágenes; cargar solo lo visible.
3. **Formatos modernos:** servir WebP/AVIF con fallback a JPG.
4. **Alt text descriptivo** para SEO y accesibilidad — usar las descripciones extraídas.
5. **Filtros** que persistan en URL (`?filtro=suites`) para compartir.
6. **CTA contextual** dentro del lightbox: si es habitación, "Reservar esta habitación"; si es salón, "Cotizar este espacio".
