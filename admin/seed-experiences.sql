-- ================================================================
-- SOL DE ORO · Tabla le_experiences + Seed inicial
-- Correr en: Supabase Dashboard → SQL Editor → New Query
-- ================================================================

-- 1. TABLA --------------------------------------------------------
CREATE TABLE le_experiences (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  mode        text NOT NULL DEFAULT 'modern',  -- 'modern' | 'business'
  cat         text NOT NULL,                   -- 'gastronomy' | 'culture' | 'shopping' | 'wellness' | 'nightlife' | 'hidden'
  zone        text,
  title       text NOT NULL,
  excerpt     text,
  tag         text,
  photo_url   text,
  maps_url    text DEFAULT '#',
  sort_order  integer DEFAULT 0,
  active      boolean DEFAULT true,
  created_at  timestamptz DEFAULT now(),
  updated_at  timestamptz DEFAULT now()
);

-- 2. RLS ----------------------------------------------------------
ALTER TABLE le_experiences ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_exp"  ON le_experiences FOR SELECT USING (true);
CREATE POLICY "admin_all_exp"    ON le_experiences FOR ALL    USING (auth.role() = 'authenticated');

-- 3. SEED — MODERN -----------------------------------------------
INSERT INTO le_experiences (mode, cat, zone, title, excerpt, tag, photo_url, maps_url, sort_order) VALUES

-- Gastronomía · Modern
('modern','gastronomy','Miraflores',
 'Maido, donde nace la cocina nikkei que el mundo aplaude.',
 'Mitsuharu Tsumura redefine el diálogo entre Japón y Perú. Reconocido como #1 de Latam por 50 Best y consistentemente en el top mundial. A 100 metros del hotel.',
 'World''s 50 Best',
 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Maido+Miraflores+Lima', 10),

('modern','gastronomy','Barranco',
 'Central: el viaje culinario más serio de Sudamérica.',
 'Virgilio Martínez traza Perú por altitudes — del mar a los Andes en 17 momentos. Best Restaurant in the World 2023. Reserva con tres meses.',
 '#1 World 2023',
 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Central+Restaurante+Barranco', 20),

('modern','gastronomy','Miraflores',
 'La Mar Cebichería, el Pacífico servido al mediodía.',
 'La cebichería más célebre de Gastón Acurio. Solo almuerzo, sin reservas, fila garantizada. Vale cada minuto de espera.',
 '★ 4.6 · 5,099 reseñas',
 'https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=La+Mar+Cebicheria+Miraflores', 30),

('modern','gastronomy','San Isidro',
 'Astrid & Gastón en Casa Moreyra: la casa madre.',
 'El buque insignia de Gastón Acurio en una casa colonial restaurada del siglo XVII. Almuerzo o cena: ambos son ceremonia.',
 'Casa Moreyra · 1740',
 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Astrid+y+Gaston+Lima', 40),

('modern','gastronomy','Miraflores',
 'Cala, donde el Pacífico se sirve en plato.',
 'Ubicación espectacular sobre la Costa Verde. Pescados a la brasa impecables y atardecer frente al océano. Reserva mesa de ventana.',
 'Pacific sunset',
 'https://images.unsplash.com/photo-1551782450-a2132b4ba21d?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Cala+Restaurante+Lima', 50),

('modern','gastronomy','Barranco',
 'Isolina, el lomo saltado que toda Lima reconoce.',
 'Cocina peruana tradicional en porciones para compartir. El lomo saltado y el flan casero son obligatorios. Barranco bohemio en su mejor versión.',
 '★ 4.5 · 1,979 reseñas',
 'https://images.unsplash.com/photo-1611143669185-af224c5e3252?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Isolina+Barranco', 60),

('modern','gastronomy','Centro Histórico',
 'Panchita, anticuchos y memoria peruana.',
 'Anticuchos, parrilla y comida criolla de Gastón Acurio en ambiente festivo. Famoso por su lomo saltado y la mejor relación calidad-precio de Lima.',
 '★ 4.5 · 5,813 reseñas',
 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Panchita+Restaurante+Miraflores', 70),

('modern','gastronomy','Miraflores',
 'Rafael Osterling, el chef que dejó huella a 20 metros.',
 'Cocina mediterránea con producto peruano en un espacio de boutique editorial. Sin pretensión, con autoridad. A pasos del hotel.',
 'Editor''s pick',
 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Rafael+Restaurante+Miraflores', 80),

('modern','gastronomy','Miraflores',
 'Cena junto a una pirámide preinca: Huaca Pucllana.',
 'Cena junto a una pirámide preinca iluminada — único en el mundo. Cocina peruana de calidad con vista a los muros de adobe del siglo V.',
 'Cena entre ruinas',
 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Restaurante+Huaca+Pucllana', 90),

('modern','gastronomy','Miraflores',
 'El Parrillón de Pablo Profumo, el templo de la carne en Lima.',
 'Considerado el mejor restaurante de carnes de Lima. Cortes argentinos y peruanos, parrilla a la vista, ambiente reservado.',
 '★ 4.8 · Top Steak Lima',
 'https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=El+Parrillon+Profumo+Miraflores', 100),

-- Cultura · Modern
('modern','culture','San Isidro',
 'Museo Larco: tres mil años de Perú en una mansión virreinal.',
 'Mansión del siglo XVIII sobre pirámide preinca del VII. Galerías de oro, plata y la colección erótica prehispánica más completa del mundo.',
 '★ 4.8 · 12,826 reseñas',
 'https://images.unsplash.com/photo-1565115021788-89e9b96bf2c2?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Museo+Larco+Lima', 110),

('modern','culture','Centro Histórico',
 'Circuito Mágico del Agua: la noche que Lima se ilumina.',
 'Trece fuentes con espectáculo de luces, agua y música. Récord Guinness por la fuente más alta del mundo. Solo de noche — pura magia.',
 '★ 4.6 · 19,341 reseñas',
 'https://images.unsplash.com/photo-1499678329028-101435549a4e?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Circuito+Magico+del+Agua+Lima', 120),

('modern','culture','Miraflores',
 'Huaca Pucllana, una pirámide en pleno Miraflores.',
 'Pirámide ceremonial de adobe del siglo V iluminada de noche, con restaurante junto a las ruinas. Tour nocturno + cena es de lo mejor de Lima.',
 'Siglo V · 7 hectáreas',
 'https://images.unsplash.com/photo-1531065208531-4036c0dba3ca?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Huaca+Pucllana+Miraflores', 130),

('modern','culture','Barranco',
 'MATE: cuando Mario Testino le regaló a Lima un museo.',
 'El museo del fotógrafo peruano más internacional, en una casa republicana restaurada. Diana, Madonna y la elite de la moda. Visita corta, impacto largo.',
 'Galería · Barranco',
 'https://images.unsplash.com/photo-1554907984-15263bfd63bd?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=MATE+Mario+Testino+Barranco', 140),

('modern','culture','Centro Histórico',
 'Convento San Francisco, catacumbas y biblioteca del XVII.',
 'Iglesia y monasterio con catacumbas que albergan más de 70,000 restos óseos, biblioteca con 25,000 volúmenes antiguos y patio de azulejos sevillanos.',
 '70,000 restos · catacumbas',
 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Convento+San+Francisco+Lima', 150),

('modern','culture','Centro Histórico',
 'Plaza Mayor: el corazón colonial de Lima.',
 'Palacio de Gobierno, Catedral fundada por Pizarro en 1535, fuente de bronce de 1650. Patrimonio Mundial UNESCO. Mejor por la mañana.',
 'UNESCO · 1535',
 'https://images.unsplash.com/photo-1531968455001-5c5272a41129?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Plaza+Mayor+Lima', 160),

('modern','culture','San Isidro',
 'MALI: 18,000 obras que cuentan la historia del arte peruano.',
 'Textiles preincas, cerámicas, pinturas virreinales y arte contemporáneo. Colección imprescindible para entender el país en una sola visita.',
 '18,000 obras · 3,000 años',
 'https://images.unsplash.com/photo-1545987796-200677ee1011?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=MALI+Museo+Arte+Lima', 170),

('modern','culture','Barranco',
 'Museo Pedro de Osma, arte virreinal en casa colonial.',
 'Casa colonial restaurada con arte virreinal andino. Visita íntima, jardines, café. Cierre perfecto antes del Puente de los Suspiros al atardecer.',
 'Editor''s pick',
 'https://images.unsplash.com/photo-1577720580479-7d839d829c73?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Museo+Pedro+de+Osma', 180),

-- Compras · Modern
('modern','shopping','Miraflores',
 'Kuna by Alpaca 111: la fibra más fina del Perú.',
 'Alpaca premium peruana — la textil más sofisticada del país. En Larcomar, frente al Pacífico. Souvenir que dura una vida.',
 'Larcomar',
 'https://images.unsplash.com/photo-1559563458-527698bf5295?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Kuna+Larcomar', 190),

('modern','shopping','Barranco',
 'Dédalo: la curaduría de diseño peruano contemporáneo.',
 'En una mansión barranquina, lo mejor del diseño peruano: cerámica, textiles, joyería, libros. Una tarde puede irse fácilmente aquí.',
 'Concept Store',
 'https://images.unsplash.com/photo-1481437156560-3205f6a55735?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Dedalo+Arte+Artesania+Barranco', 200),

('modern','shopping','Miraflores',
 'Larcomar: el shopping con el Pacífico de fondo.',
 'Centro comercial frente al océano. Marcas internacionales, restaurantes, cine, vista a los acantilados. A siete minutos caminando del hotel.',
 'A 7 min · caminando',
 'https://images.unsplash.com/photo-1519181258491-416f8fbff2d5?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Larcomar+Miraflores', 210),

-- Wellness · Modern
('modern','wellness','Miraflores',
 'Spa Sol de Oro: la mejor reset del viaje, sin moverte del hotel.',
 'Cabinas, sauna, hidromasaje. Pide la combinación Day Spa + almuerzo en Murano. Pregunta por la masajista senior — vale el upgrade.',
 'In-house · Premium',
 'images/Spa/MG_1800_ED_11zon-scaled.jpg',
 '#', 220),

('modern','wellness','Miraflores',
 'Malecón Running: diez kilómetros sobre el Pacífico.',
 'La mejor ruta de running de Lima. Diez kilómetros bordeando los acantilados con vista al océano. Mejor al amanecer, antes de las nueve.',
 '2 min · caminando',
 'https://images.unsplash.com/photo-1535007813616-79dc02ba4021?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Malecon+Miraflores', 230),

-- Vida nocturna · Modern
('modern','nightlife','Miraflores',
 'Carnaval Bar: el tercer mejor bar de Latam, a seis minutos.',
 'Coctelería de autor reconocida mundialmente. Reserva con anticipación. Ideal antes de cenar — pide la carta de pisco sours de autor.',
 '#3 Bar Latam',
 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Carnaval+Bar+Lima', 240),

('modern','nightlife','Barranco',
 'Ayahuasca Bar: coctelería en una mansión republicana.',
 'Mansión republicana convertida en bar de coctelería peruana. Patios, salones temáticos, mezcla perfecta de historia y vida nocturna.',
 'Mansion · Barranco',
 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Ayahuasca+Bar+Barranco', 250),

-- Lima oculta · Modern
('modern','hidden','Barranco',
 'Puente de los Suspiros, una leyenda en cinco segundos.',
 'Cruza el puente conteniendo la respiración: la leyenda dice que tu deseo se cumple. Después: bajada al mar por las escaleras escondidas.',
 'Sunset spot',
 'https://images.unsplash.com/photo-1518131672697-613becd4fab5?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Puente+de+los+Suspiros+Barranco', 260),

('modern','hidden','Miraflores',
 'Parque del Amor: el beso de Víctor Delfín y el Pacífico.',
 'La escultura del beso y banquetas de mosaico al estilo Gaudí frente al Pacífico. Murales con citas románticas. Imperdible al atardecer.',
 '★ 4.2 · 4,058 reseñas',
 'https://images.unsplash.com/photo-1505142468610-359e7d316be0?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Parque+del+Amor+Miraflores', 270),

('modern','hidden','Centro Histórico',
 'Casa de Aliaga: 17 generaciones bajo el mismo techo.',
 'La casa colonial más antigua de Latinoamérica (1535) — habitada continuamente por la misma familia por 17 generaciones. Visita por cita previa.',
 'Solo por cita',
 'https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Casa+de+Aliaga+Lima', 280),

('modern','hidden','Callao',
 'Islas Palomino: nadar entre lobos marinos a 40 minutos de Lima.',
 'Excursión en barco frente a Lima donde puedes nadar entre cientos de lobos marinos en su hábitat natural. Una de las experiencias más subestimadas del Perú.',
 '★ 4.6 · Adventure',
 'https://images.unsplash.com/photo-1583212292454-1fe6229603b7?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Islas+Palomino+Lima', 290),

-- 4. SEED — BUSINESS ---------------------------------------------

-- Gastronomía · Business
('business','gastronomy','San Isidro',
 'Astrid & Gastón: el power lunch perfecto en San Isidro.',
 'Casa Moreyra: ambiente sobrio, servicio impecable, mesas separadas. Reserva ventana de jardín y pide el menú ejecutivo.',
 'Power lunch',
 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Astrid+y+Gaston+Lima', 300),

('business','gastronomy','San Isidro',
 'IK Restaurant, cocina peruana moderna en ambiente reservado.',
 'Cocina peruana moderna en ambiente reservado de San Isidro. Ideal para almuerzo de negocio sin ruido. Carta de vinos peruanos seleccionada.',
 'Quiet · Business',
 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=IK+Restaurante+Lima', 310),

('business','gastronomy','Miraflores',
 'Tanta: el almuerzo express que no descuida el sabor.',
 'Comida peruana casual de alto nivel de Gastón Acurio. Perfecto para almuerzo express entre reuniones — mesa lista en treinta minutos.',
 'Express lunch',
 'https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Tanta+Restaurante+Lima', 320),

('business','gastronomy','Miraflores',
 'La Trattoria di Mambrino, cierre italiano sin estridencias.',
 'Italiana clásica de San Isidro. Ambiente íntimo, mesas distantes, ideal para cena de cierre con cliente o pareja en viaje de trabajo.',
 'Discreet · Italian',
 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=La+Trattoria+di+Mambrino', 330),

-- Cultura · Business
('business','culture','Miraflores',
 'Sol de Oro Lobby: tu oficina del día con vista a Miraflores.',
 'Nuestro propio lobby como tu oficina del día. Wi-Fi alta velocidad, café de cortesía, ambiente curado. Day Pass disponible para no huéspedes.',
 'Productive · In-hotel',
 'images/Lobby/5_5_11zon.jpg',
 '#', 340),

-- Wellness · Business
('business','wellness','Miraflores',
 'Gimnasio y piscina del hotel: el reset antes o después del día.',
 'Gimnasio Technogym y piscina al aire libre — antes o después del día laboral. Sin reserva, acceso con llave de habitación. Vista al amanecer.',
 '06:00 – 22:00',
 'images/Rooftop/PISCINA-WEB.webp',
 '#', 350),

('business','wellness','Miraflores',
 'Masaje de una hora: la mejor inversión entre reuniones.',
 'Masaje express de sesenta minutos entre meeting y meeting. Pide deep-tissue si vienes de vuelo largo. Coordinable a habitación.',
 '1h reset',
 'images/Spa/MG_1800_ED_11zon-scaled.jpg',
 '#', 360),

-- Vida nocturna · Business
('business','nightlife','Miraflores',
 'Carnaval Bar, el after office que impresiona al cliente.',
 'El bar latinoamericano #3 del mundo. Coctelería de autor para impresionar al cliente o cerrar el día con elegancia. Reserva con tiempo.',
 '#3 Bar Latam',
 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Carnaval+Bar+Lima', 370),

('business','nightlife','Miraflores',
 'Bar Murano: el pisco sour del barman de la casa.',
 'Pisco sour del barman del hotel y carta de vinos peruanos por copa. Sin necesidad de salir — el cierre perfecto del día laboral.',
 'In-hotel · Quiet',
 'images/Restaurante/13_13_11zon.jpg',
 'restaurante.html', 380),

-- Compras · Business
('business','shopping','San Isidro',
 'Av. La Mar y El Polo: shopping ejecutivo en San Isidro.',
 'Las dos avenidas con las mejores tiendas de marcas internacionales y boutiques peruanas. Ideal para un regalo express entre reuniones.',
 'Executive shopping',
 'https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Avenida+La+Mar+San+Isidro', 390),

-- Lima oculta · Business
('business','hidden','Miraflores',
 'Power walk de 30 minutos por el Malecón.',
 'Salida del hotel, Parque Kennedy, Malecón, vista al Pacífico y regreso. Treinta minutos justos para resetear la cabeza entre reuniones.',
 '30 min reset',
 'https://images.unsplash.com/photo-1535007813616-79dc02ba4021?auto=format&fit=crop&w=900&q=80',
 'https://maps.google.com/?q=Malecon+Miraflores', 400);

-- ================================================================
-- SIGUIENTE PASO:
-- 1. Refrescar el admin → sección "Experiencias" para ver los lugares
-- 2. En LeExperience.html el scroller de explorar ya carga desde esta tabla
-- ================================================================
