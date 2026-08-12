# Extracción de contenido — soldeoro.com.pe

> **Para el siguiente agente:** este paquete contiene todo el contenido del sitio actual de **Sol de Oro Hotel & Suites** (Miraflores, Lima — hotel 5★) extraído por secciones, listo para alimentar el rediseño/migración de la nueva web.
>
> Fecha de extracción: **2026-05-11**
> Fuente: https://www.soldeoro.com.pe/

---

## Estructura del paquete

```
extraccion-web/
├── README.md                    ← este archivo (índice + briefing)
├── _descargar-imagenes.ps1      ← script usado para descargar las imágenes
├── _TODO_VERIFICAR.md           ← lista de datos a confirmar con cliente antes de publicar
├── imagenes/                    ← TODAS las imágenes (~99 únicas) en una sola carpeta
├── faq/contenido.md             ← FAQ central derivada de datos verificables
└── <sección>/
    ├── contenido.md             ← extracción fiel del sitio actual
    └── complemento.md           ← información derivada que agrega valor (no inventa datos)
```

**Distinción clave** entre los dos tipos de archivos por sección:

| Archivo | Qué es | Para qué sirve |
|---|---|---|
| `contenido.md` | Extracción **fiel** del sitio en vivo, sin agregados | Fuente de verdad de lo que hay hoy |
| `complemento.md` | Reorganización + ideas estructurales basadas **solo en datos verificables** | Briefing para el rediseño de la nueva web |

Lo que **no se pudo verificar** (tarifas, política de cancelación detallada, equipo, premios, etc.) está consolidado en `_TODO_VERIFICAR.md` para que el cliente lo confirme.

---

## Índice de secciones

| # | Sección | URL original | Extracción | Complemento |
|---|---|---|---|---|
| 1 | Home | https://soldeoro.com.pe/ | [home/contenido.md](home/contenido.md) | [home/complemento.md](home/complemento.md) |
| 2 | Habitaciones | https://soldeoro.com.pe/habitaciones/ | [habitaciones/contenido.md](habitaciones/contenido.md) | [habitaciones/complemento.md](habitaciones/complemento.md) |
| 3 | Nuestro Hotel | https://soldeoro.com.pe/nuestro-hotel/ | [nuestro-hotel/contenido.md](nuestro-hotel/contenido.md) | [nuestro-hotel/complemento.md](nuestro-hotel/complemento.md) |
| 4 | Eventos | https://soldeoro.com.pe/eventos/ | [eventos/contenido.md](eventos/contenido.md) | [eventos/complemento.md](eventos/complemento.md) |
| 5 | Galería | https://soldeoro.com.pe/galeria/ | [galeria/contenido.md](galeria/contenido.md) | [galeria/complemento.md](galeria/complemento.md) |
| 6 | Ubicación | https://soldeoro.com.pe/ubicacion/ | [ubicacion/contenido.md](ubicacion/contenido.md) | [ubicacion/complemento.md](ubicacion/complemento.md) |
| 7 | Restaurante | https://soldeoro.com.pe/restaurante/ | [restaurante/contenido.md](restaurante/contenido.md) | [restaurante/complemento.md](restaurante/complemento.md) |
| 8 | Blog | https://soldeoro.com.pe/blog/ | [blog/contenido.md](blog/contenido.md) | [blog/complemento.md](blog/complemento.md) |
| 9 | **FAQ** (nueva sección sugerida) | — | [faq/contenido.md](faq/contenido.md) | — |

**No incluido** (intencional): el motor de reservas externo `https://soldeoro.ihotelier.com/...` (es un sistema de terceros, no se reescribe).

**Para el cliente — revisar antes del rediseño:** [_TODO_VERIFICAR.md](_TODO_VERIFICAR.md)

---

## Resumen del negocio (briefing rápido)

**Sol de Oro Hotel & Suites** — hotel 5★ en Miraflores, Lima, Perú.

- **Dirección:** Ca. San Martín 305, Miraflores, Lima.
- **123 habitaciones** distribuidas en 9 categorías (Standard hasta Grand Deluxe Suite con jacuzzi).
- **Restaurante propio:** Murano (cocina peruana e internacional, primer piso).
- **Espacios para eventos:** desde reuniones de 60 personas hasta conferencias de **500 personas**, más Centro de Convenciones para 300 y Salón Sol de Oro con terraza panorámica en piso 12.
- **Amenidades:** piscina al aire libre, gimnasio y spa, terraza, room service 24h, Wi-Fi gratuito, estacionamiento de 3 niveles (62 plazas).
- **Política eco:** amenities recargables, productos certificados, lavado a solicitud, uso eficiente de agua/luz.

**Posicionamiento:** lujo accesible + ubicación privilegiada (a pasos del Malecón, Larcomar, Maido — restaurante #1 de Latinoamérica).

---

## Contacto y datos clave

- **Teléfono móvil:** +51 988 861 380
- **Central:** +51 (1) 610-7000 ext. 2199
- **Email reservas:** reservas@soldeoro.pe
- **Email eventos:** comercial@soldeoro.pe
- **WhatsApp:** https://wa.link/dc0dft
- **Facebook:** https://www.facebook.com/SoldeOroHotelSuites
- **Instagram:** https://www.instagram.com/soldeorohotelsuites/

**Idiomas del sitio actual:** Español, Português Brasileiro (existe versión `/pt-br/`).

**Check-in:** 3:00 p.m. | **Check-out:** 12:00 p.m.

---

## Inventario de imágenes (~99 únicas)

Todas en `imagenes/`. Categorías:

| Categoría | Cantidad aprox. | Patrón de nombre |
|---|---|---|
| Logos y sellos | 4 | `Logo_blanco-*`, `TripAdvisor_*`, `Booking.com_*`, `Firma-staff-*` |
| Fachada / hotel general | 3 | `FACHADA.jpg`, `the-hotel-*`, `PISCINA-WEB.webp` |
| Habitaciones | 9 + extras | `JUNIOR-SUITE-*`, `FOTOS-WEB-SOL-DE-ORO-*`, `31_..40_11zon.jpg` |
| Áreas comunes / piscina / gym | ~20 | `2_2..14_14_11zon.jpg`, `FOTOS-WEB-SOL-DE-ORO-4..16` |
| Restaurante Murano | ~10 | `8_8..24_24_11zon.jpg`, `FOTOS-WEB-SOL-DE-ORO-13/15/16` |
| Salones de eventos | ~30 | `MG_*`, `IMG_*`, `EJECUTIVO-*`, `EMPRESARIALES-*`, `SOL-DE-ORO-*` |
| Planos de pisos | 3 | `Piso-I.png`, `Piso-II.png`, `Piso-12.png` |
| Iconos de distribución (montajes) | 5 | `image-1..5.jpg` |
| Banner promocional | 1 | `PAQUETES-PROMOCIONALES-SDO-22.jpg` |
| Posts del blog | 2 | `fotos-blog-1.png`, `fotos.png` |

---

## Notas para el rediseño (resumen rápido)

> Detalle ampliado en cada `<sección>/complemento.md` y en [_TODO_VERIFICAR.md](_TODO_VERIFICAR.md).

1. **Home:** las políticas ocupan demasiado espacio — moverlas a FAQ y dejar la home para conversión. Ver [home/complemento.md](home/complemento.md).
2. **Habitaciones:** falta tarifa pública, vista por categoría y fotos de baños. Hay tabla comparativa lista en [habitaciones/complemento.md](habitaciones/complemento.md).
3. **Eventos:** matriz de capacidad y selector "tipo de evento → salón" listos en [eventos/complemento.md](eventos/complemento.md).
4. **Restaurante:** la página actual está vacía visualmente. Hay fotos del Murano cruzadas desde la galería; faltan **fotos de platos**. Ver [restaurante/complemento.md](restaurante/complemento.md).
5. **Ubicación:** la página actual no tiene mapa ni guía de viaje. Complemento con clima, divisa, voltaje, propinas, transporte real desde el aeropuerto en [ubicacion/complemento.md](ubicacion/complemento.md).
6. **Galería:** algunas imágenes están mal categorizadas en el sitio actual. Re-categorización propuesta en [galeria/complemento.md](galeria/complemento.md).
7. **Blog:** solo 2 posts. Plan editorial con 6 categorías e ideas de posts iniciales en [blog/complemento.md](blog/complemento.md).
8. **Idiomas:** existe versión `/pt-br/`. Considerar añadir EN para público turístico internacional.
9. **Logo:** el archivo es `Logo_blanco-1-scaled.png` (PNG bitmap blanco). Solicitar SVG y versión a color.
10. **Reservas:** botón actual redirige a `soldeoro.ihotelier.com` (motor externo). Decidir si embebemos vía iframe/API o mantenemos redirect — ver [home/complemento.md](home/complemento.md).
11. **Capacidad de eventos:** copy del home dice "hasta 1,000 personas" pero el detalle suma máx. ~830. Verificar.

---

## Cómo regenerar la extracción

Si el sitio cambia y quieres re-extraer:
1. Re-ejecutar el flujo de WebFetch sobre las 8 URLs listadas arriba.
2. Para imágenes: editar `_descargar-imagenes.ps1` con las URLs nuevas y ejecutar:
   ```powershell
   pwsh ./_descargar-imagenes.ps1
   ```
   (o `powershell.exe` en Windows PowerShell 5.1).

---

*Generado automáticamente para alimentar el rediseño de la web del Hotel Sol de Oro.*
