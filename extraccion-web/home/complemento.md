# Home — Complemento para la nueva web

> Sugerencias de mejora basadas en datos verificables ya extraídos. Sin inventar nada, solo reorganizando y proponiendo estructura más efectiva para conversión.

---

## Diagnóstico de la home actual

**Fortalezas:**
- 9 secciones bien diferenciadas (hero, comodidades, habitaciones, políticas, restaurante, eventos, ubicación, CTA).
- Mucha información práctica (políticas, distancias, restaurantes top cerca).
- Sellos de TripAdvisor y Booking.com presentes.

**Debilidades:**
- Las **políticas** ocupan una sección entera en el home — son útiles pero deberían vivir en FAQ o en la ficha de habitación. La home necesita más conversión.
- **Habitaciones** se listan por nombre sin foto destacada ni "desde S/X". El usuario no tiene incentivo a hacer clic.
- No hay **sello de calificación visible** (Travelers' Choice + año, puntaje Booking, número de reseñas).
- No hay **prueba social** (reseñas, testimonios, certificaciones).
- El bloque de **ubicación** mezcla distancias del aeropuerto con restaurantes cercanos — separar por intención.

---

## Estructura sugerida para nueva home

| # | Bloque | Contenido (basado en datos verificados) | Objetivo |
|---|---|---|---|
| 1 | Hero | Frase: "Tu experiencia 5★ en Miraflores empieza aquí" + selector de fechas + CTA Reservar | Conversión inmediata |
| 2 | Sellos de confianza | TripAdvisor + Booking + ⚠️ premios | Confianza |
| 3 | Highlights del hotel | 5–6 íconos: 5★ · Miraflores · Restaurante · Piscina · Gimnasio · Wi-Fi | Resumen de propuesta |
| 4 | Habitaciones destacadas | 3 cards con foto + categoría + capacidad + "Desde S/⚠️" + CTA | Llevar a habitaciones |
| 5 | Restaurante Murano | Foto + 1 frase + horarios resumidos + CTA | Cross-sell gastronomía |
| 6 | Eventos | Foto del Salón Sol de Oro + capacidad + CTA cotizar | B2B |
| 7 | Ubicación | Mapa + "A pasos de" (Malecón, Larcomar, Maido) | Vender destino |
| 8 | Prueba social | ⚠️ Testimonios reales de TripAdvisor/Booking | Confianza final |
| 9 | CTA final | "¿Listo para tu próxima aventura en Lima?" + Reservar + WhatsApp | Cierre |
| 10 | Footer | Contacto, redes, idiomas (ES + PT-BR + ⚠️ EN), legales | — |

> Las políticas detalladas (cancelación, mascotas, fumadores, etc.) que actualmente están en home pasan a [`../faq/contenido.md`](../faq/contenido.md).

---

## Sellos de confianza disponibles (verificados en el sitio actual)

| Sello | Archivo local | Estado |
|---|---|---|
| TripAdvisor | [TripAdvisor_Logo.svg.png](../imagenes/TripAdvisor_Logo.svg.png) | Disponible |
| Booking.com | [Booking.com_Logo.svg.png](../imagenes/Booking.com_Logo.svg.png) | Disponible |
| Travelers' Choice | — | ⚠️ Confirmar año (el sitio actual menciona "tchotel_2021_L" en el HTML — sugiere Travelers' Choice 2021. Verificar si está vigente) |
| Categoría oficial 5★ | — | ⚠️ Confirmar categorización Mincetur |

---

## Frases / textos verificables listos para reutilizar

> Copy ya existente en el sitio que se puede mantener o adaptar.

**Hero principal (actual):**
> "Descubre Lima desde el confort y calidez de Sol de Oro Hotel & Suites"
>
> "Tu experiencia 5 estrellas en Miraflores empieza aquí. Reserva directo, al mejor precio."

**Bloque misión:**
> "Inspiración, diseño y comodidad: cada rincón fue pensado para ti."
>
> "Nuestro compromiso es hacerte sentir como en casa."

**Bloque ubicación:**
> "A solo unos pasos del Malecón de Miraflores… a pocos metros de Maido, reconocido como el Restaurante N.º 1 de Latinoamérica según 50 Best Restaurants…"

**CTA final:**
> "¿Listo para tu próxima aventura en Lima?"

---

## Bandera de **conversión directa**

El sitio actual envía la reserva a un dominio externo (`soldeoro.ihotelier.com`). Esto pierde conversión por:
1. El usuario sale del dominio y de la marca.
2. No hay manera de mostrar disponibilidad/tarifa en cada ficha de habitación.

⚠️ **Decisión clave para el cliente** (ver [`../_TODO_VERIFICAR.md`](../_TODO_VERIFICAR.md)):
- ¿Mantenemos motor externo con iframe embebido (visible dentro del sitio)?
- ¿Migramos a un motor con API que devuelva tarifas en vivo a cada ficha de habitación?
- ¿O al menos un selector de fechas en el header que pre-cargue parámetros al motor externo?
