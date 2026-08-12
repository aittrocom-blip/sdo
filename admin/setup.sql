-- ================================================================
-- SOL DE ORO · Supabase Setup
-- Correr en: Supabase Dashboard → SQL Editor → New Query
-- ================================================================

-- 1. TABLAS -------------------------------------------------------

-- Restaurantes del carrusel gastronomía (LE Experience)
CREATE TABLE le_restaurants (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name        text NOT NULL,
  label       text,
  tag         text,
  photo_url   text,
  maps_url    text,
  sort_order  integer DEFAULT 0,
  active      boolean DEFAULT true,
  created_at  timestamptz DEFAULT now(),
  updated_at  timestamptz DEFAULT now()
);

-- Lugares culturales (LE Experience)
CREATE TABLE le_cultural (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  slug        text UNIQUE NOT NULL,
  name        text NOT NULL,
  zone        text,
  teaser      text,
  description text,
  tips        jsonb DEFAULT '[]',
  photo_url   text,
  maps_url    text,
  sort_order  integer DEFAULT 0,
  active      boolean DEFAULT true,
  created_at  timestamptz DEFAULT now(),
  updated_at  timestamptz DEFAULT now()
);

-- Ofertas y promociones (página ofertas.html)
CREATE TABLE offers (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  title       text NOT NULL,
  description text,
  price       text,
  badge       text,
  image_url   text,
  expires_at  date,
  active      boolean DEFAULT true,
  sort_order  integer DEFAULT 0,
  created_at  timestamptz DEFAULT now(),
  updated_at  timestamptz DEFAULT now()
);

-- Imágenes del sitio (hero, galerías, secciones)
CREATE TABLE site_images (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  page        text NOT NULL,
  section     text NOT NULL,
  label       text,
  url         text NOT NULL,
  alt         text,
  sort_order  integer DEFAULT 0,
  updated_at  timestamptz DEFAULT now()
);

-- 2. ROW LEVEL SECURITY ------------------------------------------

ALTER TABLE le_restaurants ENABLE ROW LEVEL SECURITY;
ALTER TABLE le_cultural    ENABLE ROW LEVEL SECURITY;
ALTER TABLE offers         ENABLE ROW LEVEL SECURITY;
ALTER TABLE site_images    ENABLE ROW LEVEL SECURITY;

-- Lectura pública (páginas del sitio pueden fetchear)
CREATE POLICY "public_read_restaurants" ON le_restaurants FOR SELECT USING (true);
CREATE POLICY "public_read_cultural"    ON le_cultural    FOR SELECT USING (true);
CREATE POLICY "public_read_offers"      ON offers         FOR SELECT USING (true);
CREATE POLICY "public_read_images"      ON site_images    FOR SELECT USING (true);

-- Escritura solo para admins autenticados
CREATE POLICY "admin_all_restaurants" ON le_restaurants FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "admin_all_cultural"    ON le_cultural    FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "admin_all_offers"      ON offers         FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "admin_all_images"      ON site_images    FOR ALL USING (auth.role() = 'authenticated');

-- 3. DATOS INICIALES — RESTAURANTES ------------------------------

INSERT INTO le_restaurants (name, label, tag, photo_url, maps_url, sort_order) VALUES
('Maido',           'Nikkei · Miraflores',          '#1 Latinoamérica · 50 Best',    'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=900&q=80', 'https://maps.google.com/?q=Maido+Miraflores+Lima', 1),
('Central',         'Alturas · Barranco',            '#1 Mundo 2023 · 50 Best',       'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=900&q=80', 'https://maps.google.com/?q=Central+Restaurante+Barranco', 2),
('La Mar',          'Cebichería · Miraflores',       '★ 4.6 · 5,099 reseñas',         'https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=900&q=80', 'https://maps.google.com/?q=La+Mar+Cebicheria+Miraflores', 3),
('Rafael',          'Mediterráneo · Miraflores',     'Editor''s pick · A 20 m',       'https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=900&q=80', 'https://maps.google.com/?q=Rafael+Restaurante+Miraflores', 4),
('Astrid & Gastón', 'Alta cocina · San Isidro',      'Casa Moreyra · 1740',           'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=80', 'https://maps.google.com/?q=Astrid+y+Gaston+Lima', 5),
('El Parrillón',    'Parrilla · Miraflores',         '★ 4.8 · Mejor steak Lima',      'https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=900&q=80', 'https://maps.google.com/?q=El+Parrillon+Profumo+Miraflores', 6),
('Isolina',         'Criolla · Barranco',            '★ 4.5 · 1,979 reseñas',         'https://images.unsplash.com/photo-1611143669185-af224c5e3252?auto=format&fit=crop&w=900&q=80', 'https://maps.google.com/?q=Isolina+Barranco', 7),
('Huaca Pucllana',  'Cena · ruinas · Miraflores',   'Pirámide siglo V iluminada',    'https://images.unsplash.com/photo-1531065208531-4036c0dba3ca?auto=format&fit=crop&w=900&q=80', 'https://maps.google.com/?q=Restaurante+Huaca+Pucllana', 8);

-- 4. DATOS INICIALES — CULTURALES --------------------------------

INSERT INTO le_cultural (slug, name, zone, teaser, description, tips, photo_url, maps_url, sort_order) VALUES
('larco', 'Museo Larco', 'San Isidro · 15 min en taxi',
 'Mansión del s.XVIII sobre pirámide preinca. Colección de oro, plata y la galería erótica prehispánica más completa del mundo.',
 'Una mansión virreinal del siglo XVIII construida sobre una pirámide preinca del siglo VII. Alberga la mayor colección de oro y plata prehispánica del mundo — más de 45,000 piezas catalogadas — y la célebre galería erótica, la más completa de cualquier civilización precolombina.',
 '["Llega temprano: abre a las 9 AM y se llena antes del mediodía","El café del museo tiene jardines coloniales perfectos para el brunch","La visita completa toma 2-3 horas; la galería de textiles es de las mejores del mundo","El concierge puede coordinar transporte y entradas"]',
 'https://images.unsplash.com/photo-1565115021788-89e9b96bf2c2?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Museo+Larco+Lima', 1),

('huaca', 'Huaca Pucllana', 'Miraflores · 2 min a pie del hotel',
 'Pirámide de adobe del siglo V en pleno Miraflores. De noche se ilumina — cenar junto a las ruinas es único en el mundo.',
 'Una pirámide ceremonial de adobe del siglo V d.C. en pleno corazón de Miraflores — a pasos del hotel. De noche se ilumina y el espectáculo es único: cenar en el restaurante junto a los muros milenarios iluminados es una de las experiencias más especiales de Lima.',
 '["El tour nocturno comienza al atardecer — la entrada más mágica","Reserva cena en el restaurante Huaca Pucllana para la experiencia completa","Disponible tour diurno para ver la pirámide desde arriba","Pregunta al concierge por el tour guiado en español o inglés"]',
 'https://images.unsplash.com/photo-1531065208531-4036c0dba3ca?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Huaca+Pucllana+Miraflores', 2),

('sanfrancisco', 'Convento San Francisco', 'Centro Histórico · 25 min en taxi',
 'Catacumbas con 70,000 restos, biblioteca del s.XVII y patio de azulejos sevillanos de 1600.',
 'Iglesia y monasterio barroco construido en 1673. Bajo el suelo, catacumbas que albergan más de 70,000 restos óseos ordenados en patrones geométricos. En la superficie: una biblioteca con 25,000 volúmenes del siglo XVII y un patio interior decorado con azulejos sevillanos del 1600.',
 '["Visita obligatoria las catacumbas — son únicas en Sudamérica","Combinar con la Plaza Mayor al lado para una mañana completa","El tour guiado incluido con la entrada vale la pena","Mejor de mañana, antes del mediodía"]',
 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Convento+San+Francisco+Lima', 3),

('mate', 'MATE · Mario Testino', 'Barranco · 20 min en taxi',
 'El museo del fotógrafo peruano más internacional, en una casa republicana restaurada en Barranco.',
 'El museo del fotógrafo peruano más famoso del mundo, en una casa republicana restaurada en el corazón bohemio de Barranco. Retratos de Diana, Madonna, Kate Moss y la élite de la moda mundial conviven con series sobre la identidad peruana.',
 '["Combinar con almuerzo en Barranco y el Puente de los Suspiros al atardecer","La tienda del museo tiene los mejores libros fotográficos de Lima","Exposiciones temporales que rotan cada 3-4 meses","La caminata por Barranco desde aquí es de las mejores de la ciudad"]',
 'https://images.unsplash.com/photo-1554907984-15263bfd63bd?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=MATE+Mario+Testino+Barranco', 4),

('plaza', 'Plaza Mayor de Lima', 'Centro Histórico · 25 min en taxi',
 'El corazón fundacional de Lima, trazado por Pizarro en 1535. Catedral, Palacio de Gobierno y fuente de bronce de 1650. Patrimonio UNESCO.',
 'El corazón fundacional de Lima, trazado por Francisco Pizarro en 1535. La Catedral, el Palacio de Gobierno y la fuente de bronce de 1650 enmarcan una de las plazas coloniales más imponentes de América. Todo el centro histórico fue declarado Patrimonio Mundial UNESCO en 1988.',
 '["Visita preferiblemente al amanecer — la luz es extraordinaria y hay menos turistas","El cambio de guardia en el Palacio de Gobierno es espectáculo obligatorio","Combinar con el Convento San Francisco a dos cuadras","Cuidado con el tráfico: el taxi te deja en la plaza directamente"]',
 'https://images.unsplash.com/photo-1531968455001-5c5272a41129?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Plaza+Mayor+Lima', 5),

('aliaga', 'Casa de Aliaga', 'Centro Histórico · 30 min en taxi',
 'La casa colonial más antigua de Latinoamérica (1535), habitada por la misma familia durante 17 generaciones. Solo por cita previa.',
 'Construida en 1535 sobre el antiguo palacio del cacique Taulichusco, es la casa colonial más antigua de Latinoamérica aún habitada. Dieciséis generaciones de la misma familia han vivido aquí sin interrupción. Solo se visita por cita previa — lo que la convierte en una experiencia verdaderamente exclusiva.',
 '["Solo por cita previa — el concierge puede coordinar la visita","La visita guiada por la familia propietaria es una experiencia única","Combinar con la Plaza Mayor al lado para una mañana completa","Cupos muy limitados: reservar con varios días de anticipación"]',
 'https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Casa+de+Aliaga+Lima', 6);

-- ================================================================
-- SIGUIENTE PASO:
-- 1. Ir a Supabase → Authentication → Users → Invite User
--    (crear el usuario admin con tu email)
-- 2. Copiar tu Project URL y anon key desde Settings → API
-- 3. Pegarlos en admin/index.html donde dice TU_SUPABASE_URL
-- ================================================================
