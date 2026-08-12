-- ================================================================
-- SOL DE ORO · Tabla site_content + Seed inicial
-- Correr en: Supabase Dashboard → SQL Editor → New Query
-- ================================================================

-- 1. TABLA --------------------------------------------------------
CREATE TABLE site_content (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  page        text NOT NULL,
  section     text NOT NULL,
  key         text NOT NULL,
  label       text,
  value       text,
  type        text DEFAULT 'text',   -- 'text' | 'textarea' | 'url'
  sort_order  integer DEFAULT 0,
  updated_at  timestamptz DEFAULT now()
);

-- 2. RLS ----------------------------------------------------------
ALTER TABLE site_content ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_content"  ON site_content FOR SELECT USING (true);
CREATE POLICY "admin_all_content"    ON site_content FOR ALL    USING (auth.role() = 'authenticated');

-- 3. SEED ---------------------------------------------------------

INSERT INTO site_content (page, section, key, label, value, type, sort_order) VALUES

-- ================================================================
-- INICIO (index.html) · Hero Slide 1 — Miraflores
-- ================================================================
('index','hero','slide1-eyebrow',    'Slide 1 · Eyebrow',     'Ubicación Privilegiada',                                                         'text',     1),
('index','hero','slide1-titulo',     'Slide 1 · Título',      'En el corazón de Miraflores, a pasos del mar.',                                  'text',     2),
('index','hero','slide1-descripcion','Slide 1 · Descripción', 'Malecón, Larcomar, Parque Kennedy y los mejores restaurantes de Lima — todo a minutos caminando desde el hotel.', 'textarea', 3),
('index','hero','slide1-cta',        'Slide 1 · CTA texto',   'Ver ubicación',                                                                  'text',     4),
('index','hero','slide1-cta-link',   'Slide 1 · CTA enlace',  'ubicacion.html',                                                                 'url',      5),

-- Hero Slide 2 — Habitaciones
('index','hero','slide2-eyebrow',    'Slide 2 · Eyebrow',     'Cinco Estrellas · Miraflores',                                                   'text',     6),
('index','hero','slide2-titulo',     'Slide 2 · Título',      'El descanso que tu viaje a Lima merece.',                                        'text',     7),
('index','hero','slide2-descripcion','Slide 2 · Descripción', 'Habitaciones diseñadas para dormir bien: cama king, blackout completo y el silencio de Miraflores a pasos del Pacífico.', 'textarea', 8),
('index','hero','slide2-cta',        'Slide 2 · CTA texto',   'Ver habitaciones',                                                               'text',     9),
('index','hero','slide2-cta-link',   'Slide 2 · CTA enlace',  'habitaciones.html',                                                              'url',      10),

-- Hero Slide 3 — Eventos
('index','hero','slide3-eyebrow',    'Slide 3 · Eyebrow',     'Salones & Banquetes',                                                            'text',     11),
('index','hero','slide3-titulo',     'Slide 3 · Título',      'Eventos memorables hasta para mil invitados en el centro de Miraflores.',         'text',     12),
('index','hero','slide3-descripcion','Slide 3 · Descripción', 'Salones modulares, directorios ejecutivos y catering peruano para bodas, conferencias y celebraciones.', 'textarea', 13),
('index','hero','slide3-cta',        'Slide 3 · CTA texto',   'Ver salones',                                                                    'text',     14),
('index','hero','slide3-cta-link',   'Slide 3 · CTA enlace',  'eventos.html',                                                                   'url',      15),

-- Hero Slide 4 — Restaurante
('index','hero','slide4-eyebrow',    'Slide 4 · Eyebrow',     'Restaurante Murano',                                                             'text',     16),
('index','hero','slide4-titulo',     'Slide 4 · Título',      'Cocina peruana de autor en una mesa con vista al Pacífico.',                     'text',     17),
('index','hero','slide4-descripcion','Slide 4 · Descripción', 'Una sola mesa donde dialogan los productos del mar y los valles andinos. Abierto al público, todos los días.', 'textarea', 18),
('index','hero','slide4-cta',        'Slide 4 · CTA texto',   'Reservar mesa',                                                                  'text',     19),
('index','hero','slide4-cta-link',   'Slide 4 · CTA enlace',  'restaurante.html',                                                               'url',      20),

-- ================================================================
-- INICIO · Sección Feature
-- ================================================================
('index','feature','titulo-seccion',   'Título de sección',  'El hotel',                                                                        'text',     1),
('index','feature','feature1-titulo',  'Feature 1 · Título', 'Arquitectura & Diseño',                                                           'text',     2),
('index','feature','feature2-titulo',  'Feature 2 · Título', 'Habitaciones',                                                                    'text',     3),
('index','feature','feature3-titulo',  'Feature 3 · Título', 'Restaurante Murano',                                                              'text',     4),
('index','feature','feature4-titulo',  'Feature 4 · Título', 'Spa & Servicios',                                                                 'text',     5),
('index','feature','feature5-titulo',  'Feature 5 · Título', 'Salones de Eventos',                                                              'text',     6),

-- ================================================================
-- HABITACIONES (habitaciones.html) · Hero
-- ================================================================
('habitaciones','hero','eyebrow',      'Eyebrow',             'Habitaciones · 123 unidades',                                                    'text',     1),
('habitaciones','hero','titulo',       'Título',              'Nueve categorías para descansar como en casa.',                                   'text',     2),
('habitaciones','hero','descripcion',  'Descripción',         'Desde la Standard hasta la Grand Deluxe Suite. Todas con WiFi de alta velocidad, baño en mármol travertino, caja de seguridad y la luz natural de Miraflores.', 'textarea', 3),
('habitaciones','hero','cta',          'CTA texto',           'Explorar categorías',                                                             'text',     4),

-- ================================================================
-- HABITACIONES · Habitaciones individuales
-- ================================================================
('habitaciones','room','room1-nombre',    'Estándar King · Nombre',    'Estándar King',                                                          'text',     1),
('habitaciones','room','room1-precio',    'Estándar King · Precio',    'Desde S/ 320 por noche',                                                 'text',     2),
('habitaciones','room','room2-nombre',    'Estándar Twin · Nombre',    'Estándar Twin',                                                          'text',     3),
('habitaciones','room','room3-nombre',    'Superior King · Nombre',    'Superior King',                                                          'text',     4),
('habitaciones','room','room4-nombre',    'Superior Twin · Nombre',    'Superior Twin',                                                          'text',     5),
('habitaciones','room','room5-nombre',    'Junior Suite · Nombre',     'Junior Suite',                                                           'text',     6),
('habitaciones','room','room6-nombre',    'Junior Suite Twin · Nombre','Junior Suite Twin',                                                      'text',     7),
('habitaciones','room','room7-nombre',    'Ejecutiva · Nombre',        'Ejecutiva',                                                              'text',     8),
('habitaciones','room','room8-nombre',    'Deluxe · Nombre',           'Deluxe',                                                                 'text',     9),
('habitaciones','room','room9-nombre',    'Grand Deluxe · Nombre',     'Grand Deluxe Suite',                                                     'text',     10),

-- ================================================================
-- RESTAURANTE (restaurante.html) · Hero
-- ================================================================
('restaurante','hero','eyebrow',       'Eyebrow',             'Murano · Cocina peruana de autor',                                               'text',     1),
('restaurante','hero','titulo',        'Título',              'Una mesa abierta al público, todos los días del año.',                            'text',     2),
('restaurante','hero','descripcion',   'Descripción',         'Productos del mar y los valles andinos dialogan en cada plato. Desayuno buffet, almuerzo ejecutivo y cena degustación con maridaje de vinos peruanos.', 'textarea', 3),

-- ================================================================
-- RESTAURANTE · Platos del menú
-- ================================================================
('restaurante','platos','plato1-nombre', 'Plato 1 · Nombre',  'Atún sellado al sésamo',                                                         'text',     1),
('restaurante','platos','plato2-nombre', 'Plato 2 · Nombre',  'Lomo saltado',                                                                   'text',     2),
('restaurante','platos','plato3-nombre', 'Plato 3 · Nombre',  'Crostinis de jamón',                                                             'text',     3),
('restaurante','platos','plato4-nombre', 'Plato 4 · Nombre',  'Pulpo a la parrilla',                                                            'text',     4),
('restaurante','platos','plato5-nombre', 'Plato 5 · Nombre',  'Tabla de Quesos & Charcutería',                                                  'text',     5),

-- ================================================================
-- EVENTOS (eventos.html) · Hero
-- ================================================================
('eventos','hero','eyebrow',           'Eyebrow',             '7 salones · 980 personas · 1.458 m²',                                            'text',     1),
('eventos','hero','titulo',            'Título',              'Eventos memorables en el corazón de Miraflores.',                                 'text',     2),
('eventos','hero','descripcion',       'Descripción',         'Tres pisos de salones equipados, indoor + outdoor. Desde reuniones íntimas hasta convenciones de 500 personas. Tecnología avanzada, atención personalizada y la cocina del Restaurante Murano.', 'textarea', 3),

-- ================================================================
-- EVENTOS · Salones
-- ================================================================
('eventos','salon','salon1-nombre',    'Salón 1 · Nombre',    'Ejecutivo I',                                                                    'text',     1),
('eventos','salon','salon2-nombre',    'Salón 2 · Nombre',    'Ejecutivo II',                                                                   'text',     2),
('eventos','salon','salon3-nombre',    'Salón 3 · Nombre',    'Ejecutivo III',                                                                  'text',     3),
('eventos','salon','salon4-nombre',    'Salón 4 · Nombre',    'Empresarial I',                                                                  'text',     4),
('eventos','salon','salon5-nombre',    'Salón 5 · Nombre',    'Empresarial II',                                                                 'text',     5),
('eventos','salon','salon6-nombre',    'Salón 6 · Nombre',    'Sol de Oro',                                                                     'text',     6),
('eventos','salon','salon7-nombre',    'Salón 7 · Nombre',    'Centro de Convenciones',                                                         'text',     7),

-- ================================================================
-- SERVICIOS (servicios.html) · Hero
-- ================================================================
('servicios','hero','eyebrow',         'Eyebrow',             'Servicios & Amenidades',                                                          'text',     1),
('servicios','hero','titulo',          'Título',              'Doce servicios incluidos en tu estadía.',                                         'text',     2),
('servicios','hero','descripcion',     'Descripción',         'WiFi en todo el hotel, atención bilingüe 24/7 y la cocina del Restaurante Murano siempre cerca. Sin recargos sorpresa, sin letras chicas.', 'textarea', 3),

-- ================================================================
-- OFERTAS (ofertas.html) · Hero
-- ================================================================
('ofertas','hero','eyebrow',           'Eyebrow',             'Ofertas & Promociones',                                                           'text',     1),
('ofertas','hero','titulo',            'Título',              'Las mejores tarifas, directo desde el hotel.',                                    'text',     2),
('ofertas','hero','descripcion',       'Descripción',         'Reserva directo y accede a tarifas exclusivas, upgrades y beneficios que no encontrarás en ningún otro canal.', 'textarea', 3);

-- ================================================================
-- SIGUIENTE PASO:
-- 1. Ejecutar también admin/seed-images.sql si aún no lo has hecho
-- 2. Refrescar el admin → sección "Páginas" para ver imagen + contenido
-- ================================================================
