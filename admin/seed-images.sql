-- ================================================================
-- SOL DE ORO · Seed de imágenes del sitio
-- Correr en: Supabase Dashboard → SQL Editor → New Query
-- ================================================================

INSERT INTO site_images (page, section, label, url, alt, sort_order) VALUES

-- ================================================================
-- INICIO (index.html)
-- ================================================================
('index','hero','Slide Miraflores',          'images/Exterior/fotomiraflores.jpg',                     'Vista de Miraflores desde el hotel', 1),
('index','hero','Slide Habitación',          'images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-2_11zon.jpg',   'Habitación superior king', 2),
('index','hero','Slide Eventos',             'images/Eventos/32_11zon.jpg',                            'Salón de eventos', 3),
('index','hero','Slide Restaurante',         'images/Restaurante/14_14_11zon.jpg',                     'Restaurante Murano', 4),

('index','feature','Arquitectura / Fachada', 'images/Exterior/FACHADA.jpg',                           'Fachada del hotel', 1),
('index','feature','Habitaciones',           'images/Habitaciones/JUNIOR-SUITE_11zon.jpg',             'Junior Suite', 2),
('index','feature','Restaurante Murano',     'images/Restaurante/13_13_11zon.jpg',                     'Bar Murano interior', 3),
('index','feature','Servicios / Spa',        'images/Spa/MG_1800_ED_11zon-scaled.jpg',                 'Área de spa', 4),
('index','feature','Eventos corporativos',   'images/Eventos/EMPRESARIALES-I_7_11zon.jpg',             'Salón empresarial', 5),

('index','gallery','Lobby',                  'images/Lobby/5_5_11zon.jpg',                             'Lobby del hotel', 1),
('index','gallery','Restaurante barra',      'images/Restaurante/24_24_11zon.jpg',                     'Barra del restaurante', 2),
('index','gallery','Piscina Rooftop',        'images/Rooftop/PISCINA-WEB.webp',                       'Piscina del rooftop', 3),
('index','gallery','Gimnasio',               'images/Gimnasio/4_4_11zon.jpg',                          'Área de gimnasio', 4),
('index','gallery','Rooftop vista',          'images/Rooftop/9_9_11zon.jpg',                           'Vista desde el rooftop', 5),

('index','promo','Habitación promoción',     'images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-2_11zon.jpg',  'Habitación en promoción', 1),
('index','promo','Restaurante promoción',    'images/Restaurante/23_23_11zon.jpg',                     'Menú especial', 2),
('index','promo','Spa promoción',            'images/Spa/MG_1800_ED_11zon-scaled.jpg',                 'Paquete spa', 3),

-- ================================================================
-- HABITACIONES (habitaciones.html)
-- ================================================================
('habitaciones','hero','Banner principal',   'images/Habitaciones/JUNIOR-SUITE-TWIN_11zon.jpg',        'Vista habitaciones', 1),

('habitaciones','room','Estándar King',      'images/Habitaciones/FOTOS-WEB-SOL-DE-ORO_11zon-1.jpg',  'Habitación estándar king', 1),
('habitaciones','room','Estándar Twin',      'images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-1_2_11zon.jpg','Habitación estándar twin', 2),
('habitaciones','room','Superior King',      'images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-2_11zon.jpg',  'Habitación superior king', 3),
('habitaciones','room','Superior Twin',      'images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-3_11zon.jpg',  'Habitación superior twin', 4),
('habitaciones','room','Junior Suite',       'images/Habitaciones/JUNIOR-SUITE_11zon.jpg',             'Junior suite', 5),
('habitaciones','room','Junior Suite Twin',  'images/Habitaciones/JUNIOR-SUITE-TWIN_11zon.jpg',        'Junior suite twin', 6),
('habitaciones','room','Ejecutiva',          'images/Habitaciones/FOTOS-WEB-SOL-DE-ORO_11zon.jpg',    'Habitación ejecutiva', 7),
('habitaciones','room','Deluxe',             'images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-5_11zon.jpg',  'Habitación deluxe', 8),
('habitaciones','room','Grand Deluxe',       'images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-3_11zon-1.jpg','Habitación grand deluxe', 9),

-- ================================================================
-- RESTAURANTE (restaurante.html)
-- ================================================================
('restaurante','hero','Banner Murano',       'images/Restaurante/14_14_11zon.jpg',                     'Restaurante Murano', 1),
('restaurante','murano','Interior principal','images/Restaurante/12_12_11zon.jpg',                     'Interior Murano', 1),
('restaurante','platos','Atún sellado',      'images/Restaurante/FOTOS-WEB-SOL-DE-ORO-9_11_11zon.jpg','Atún sellado al sésamo', 1),
('restaurante','platos','Lomo saltado',      'images/Restaurante/FOTOS-WEB-SOL-DE-ORO-10_10_11zon.jpg','Lomo saltado', 2),
('restaurante','platos','Crostinis jamón',   'images/Restaurante/FOTOS-WEB-SOL-DE-ORO-12_8_11zon.jpg','Crostinis de jamón', 3),
('restaurante','platos','Pulpo a la parrilla','images/Restaurante/FOTOS-WEB-SOL-DE-ORO-11_9_11zon.jpg','Pulpo a la parrilla', 4),
('restaurante','platos','Tabla charcutería', 'images/Restaurante/IMG_3832_ED_9_11zon-scaled.jpg',      'Tabla de quesos y charcutería', 5),

-- ================================================================
-- EVENTOS (eventos.html)
-- ================================================================
('eventos','hero','Banner eventos',          'images/Eventos/EMPRESARIALES-I_7_11zon.jpg',             'Salón de eventos corporativos', 1),
('eventos','salon','Ejecutivo I foto 1',     'images/Eventos/IMG_8388_25_11zon-scaled.jpg',            'Salón Ejecutivo I', 1),
('eventos','salon','Ejecutivo II auditorio', 'images/Eventos/EJECUTIVO-II-AUDITORIO_2_11zon-scaled.jpg','Salón Ejecutivo II auditorio', 2),
('eventos','salon','Ejecutivo III',          'images/Eventos/MG_2145_ED-v2_5_11zon-scaled.jpg',        'Salón Ejecutivo III', 3),
('eventos','salon','Empresarial I',          'images/Eventos/EMPRESARIALES-I_7_11zon.jpg',             'Salón Empresarial I', 4),
('eventos','salon','Empresarial II',         'images/Eventos/EMPRESARIALES-II_10_11zon.jpg',           'Salón Empresarial II', 5),
('eventos','salon','Empresarial III',        'images/Eventos/IMG_2226_ED_8_11zon-scaled.jpg',          'Salón Empresarial III', 6),
('eventos','salon','Empresarial completo',   'images/Eventos/Empresariales-Aud-8-1_3_11zon-scaled.jpg','Salón Empresarial completo', 7),
('eventos','salon','Sol de Oro',             'images/Eventos/SOL-DE-ORO-MESAS-REDONDAS-1.jpeg',        'Salón Sol de Oro mesas redondas', 8),
('eventos','salon','Centro Convenciones',    'images/Eventos/MG_2588_edi2-scaled.jpg',                 'Centro de convenciones', 9),

-- ================================================================
-- SERVICIOS / SPA (servicios.html)
-- ================================================================
('servicios','hero','Banner spa & wellness', 'images/Spa/MG_1800_ED_11zon-scaled.jpg',                 'Área de spa y wellness', 1),
('servicios','feature','Piscina Rooftop',    'images/Rooftop/PISCINA-WEB.webp',                       'Piscina en el rooftop', 1),

-- ================================================================
-- OFERTAS (ofertas.html)
-- ================================================================
('ofertas','hero','Banner ofertas',          'images/Restaurante/24_24_11zon.jpg',                     'Ofertas y promociones', 1),
('ofertas','promo','Habitación oferta',      'images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-2_11zon.jpg',  'Oferta habitación', 1),
('ofertas','promo','Restaurante oferta',     'images/Restaurante/23_23_11zon.jpg',                     'Oferta restaurante', 2),
('ofertas','promo','Spa oferta',             'images/Spa/MG_1800_ED_11zon-scaled.jpg',                 'Oferta spa', 3),
('ofertas','promo','Habitación deluxe',      'images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-5_11zon.jpg',  'Habitación deluxe oferta', 4),
('ofertas','promo','Junior suite twin',      'images/Habitaciones/JUNIOR-SUITE-TWIN_11zon.jpg',        'Junior suite twin oferta', 5),
('ofertas','promo','Eventos oferta',         'images/Eventos/EMPRESARIALES-I_7_11zon.jpg',             'Paquete eventos', 6),

-- ================================================================
-- ACERCA (acerca.html)
-- ================================================================
('acerca','hero','Banner nosotros',          'images/Exterior/the-hotel-v13828831_ED.webp',            'Hotel Sol de Oro exterior', 1),
('acerca','feature','Historia fachada',      'images/Exterior/FACHADA.jpg',                            'Fachada histórica del hotel', 1),
('acerca','feature','Equipo lobby',          'images/Lobby/6_6_11zon.jpg',                             'Lobby y equipo', 2),

-- ================================================================
-- COMPARTIDAS (todas las páginas)
-- ================================================================
('shared','band','Premio / Rooftop oscuro',  'images/Rooftop/11_11_11zon-dark.jpg',                    'Banda de reconocimientos', 1);
