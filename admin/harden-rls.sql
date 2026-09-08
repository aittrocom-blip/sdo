-- ================================================================
-- SOL DE ORO · Endurecer RLS: solo admins reales pueden escribir
-- Correr en: Supabase Dashboard → SQL Editor → New Query
--
-- Problema que corrige: las políticas "admin_all_*" actuales usan
-- auth.role() = 'authenticated', que es cualquier usuario logueado
-- en el proyecto (no necesariamente vos). Esto las reemplaza por
-- una tabla `admins` explícita.
-- ================================================================

-- 1. TABLA DE ADMINS -----------------------------------------------
CREATE TABLE IF NOT EXISTS admins (
  user_id     uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email       text,
  created_at  timestamptz DEFAULT now()
);
ALTER TABLE admins ENABLE ROW LEVEL SECURITY;
-- Nadie necesita leer esta tabla desde el cliente; sin políticas de
-- SELECT, queda cerrada por defecto (RLS deniega todo lo no permitido).

-- Te agrega como admin buscando tu usuario por email.
-- Requisito: ya debés existir en Authentication → Users con este email
-- (si todavía no te invitaste a vos mismo, hacelo antes de correr esto).
INSERT INTO admins (user_id, email)
SELECT id, email FROM auth.users WHERE email = 'bittig.patrick@gmail.com'
ON CONFLICT (user_id) DO NOTHING;

-- Si el INSERT anterior no agregó ninguna fila, es porque ese email
-- todavía no existe en auth.users — anda a Authentication → Users →
-- Invite User primero, y después volvé a correr solo este INSERT.

-- 2. REEMPLAZAR LAS POLÍTICAS DE ESCRITURA --------------------------
-- Mismo patrón para las 7 tablas: la lectura pública (public_read_*)
-- no se toca, solo se reemplaza la de escritura (admin_all_*).

DROP POLICY IF EXISTS "admin_all_restaurants" ON le_restaurants;
CREATE POLICY "admin_all_restaurants" ON le_restaurants FOR ALL
  USING (auth.uid() IN (SELECT user_id FROM admins))
  WITH CHECK (auth.uid() IN (SELECT user_id FROM admins));

DROP POLICY IF EXISTS "admin_all_cultural" ON le_cultural;
CREATE POLICY "admin_all_cultural" ON le_cultural FOR ALL
  USING (auth.uid() IN (SELECT user_id FROM admins))
  WITH CHECK (auth.uid() IN (SELECT user_id FROM admins));

DROP POLICY IF EXISTS "admin_all_offers" ON offers;
CREATE POLICY "admin_all_offers" ON offers FOR ALL
  USING (auth.uid() IN (SELECT user_id FROM admins))
  WITH CHECK (auth.uid() IN (SELECT user_id FROM admins));

DROP POLICY IF EXISTS "admin_all_images" ON site_images;
CREATE POLICY "admin_all_images" ON site_images FOR ALL
  USING (auth.uid() IN (SELECT user_id FROM admins))
  WITH CHECK (auth.uid() IN (SELECT user_id FROM admins));

DROP POLICY IF EXISTS "admin_all_content" ON site_content;
CREATE POLICY "admin_all_content" ON site_content FOR ALL
  USING (auth.uid() IN (SELECT user_id FROM admins))
  WITH CHECK (auth.uid() IN (SELECT user_id FROM admins));

DROP POLICY IF EXISTS "admin_all_popups" ON popups;
CREATE POLICY "admin_all_popups" ON popups FOR ALL
  USING (auth.uid() IN (SELECT user_id FROM admins))
  WITH CHECK (auth.uid() IN (SELECT user_id FROM admins));

-- Nota: le_experiences no tiene un CREATE TABLE en este repo (se creó
-- directo en el dashboard), así que no sé el nombre exacto de su
-- política de escritura. Si existe, reemplazala a mano con el mismo
-- patrón, ej.:
--   DROP POLICY IF EXISTS "<nombre que tenga>" ON le_experiences;
--   CREATE POLICY "admin_all_experiences" ON le_experiences FOR ALL
--     USING (auth.uid() IN (SELECT user_id FROM admins))
--     WITH CHECK (auth.uid() IN (SELECT user_id FROM admins));

-- 3. STORAGE ---------------------------------------------------------
DROP POLICY IF EXISTS "admin_write_popups_storage" ON storage.objects;
CREATE POLICY "admin_write_popups_storage" ON storage.objects FOR ALL
  USING (bucket_id = 'popups' AND auth.uid() IN (SELECT user_id FROM admins))
  WITH CHECK (bucket_id = 'popups' AND auth.uid() IN (SELECT user_id FROM admins));

-- El bucket "experiences" se creó fuera de este repo (por dashboard),
-- así que no puedo saber el nombre de su política actual desde acá.
-- Revisalo en Storage → experiences → Policies y aplicá el mismo
-- reemplazo (bucket_id = 'experiences' en vez de 'popups').

-- ================================================================
-- VERIFICACIÓN
-- Corré esto después y confirmá que aparezca tu email:
--   SELECT * FROM admins;
-- Si en algún momento invitás a alguien más del equipo a administrar
-- el sitio, agregalo con el mismo patrón del INSERT de arriba.
-- ================================================================
