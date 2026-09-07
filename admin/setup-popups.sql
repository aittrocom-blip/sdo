-- ================================================================
-- SOL DE ORO · Tabla popups + Storage bucket
-- Correr en: Supabase Dashboard → SQL Editor → New Query
-- ================================================================

-- 1. TABLA --------------------------------------------------------
CREATE TABLE popups (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  title       text,             -- solo referencia interna en el admin, no se muestra al visitante
  image_url   text NOT NULL,
  link_url    text,             -- opcional: si está vacío, el popup no es clickeable
  starts_on   date NOT NULL,
  ends_on     date NOT NULL,
  active      boolean DEFAULT true,
  created_at  timestamptz DEFAULT now(),
  updated_at  timestamptz DEFAULT now()
);

-- 2. ROW LEVEL SECURITY --------------------------------------------
ALTER TABLE popups ENABLE ROW LEVEL SECURITY;

-- Lectura pública (el sitio consulta esto en cada página)
CREATE POLICY "public_read_popups" ON popups FOR SELECT USING (true);

-- Escritura solo para admins autenticados
CREATE POLICY "admin_all_popups" ON popups FOR ALL USING (auth.role() = 'authenticated');

-- 3. STORAGE BUCKET -------------------------------------------------
-- Mismo patrón que el bucket "experiences" ya usado por el admin.
INSERT INTO storage.buckets (id, name, public)
VALUES ('popups', 'popups', true)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "public_read_popups_storage" ON storage.objects
  FOR SELECT USING (bucket_id = 'popups');

CREATE POLICY "admin_write_popups_storage" ON storage.objects
  FOR ALL USING (bucket_id = 'popups' AND auth.role() = 'authenticated');

-- ================================================================
-- SIGUIENTE PASO:
-- 1. Refrescar admin/index.html → nueva sección "Popup" en el menú.
-- 2. Crear el primer popup (foto + link + rango de fechas).
-- 3. El sitio público lo muestra solo si hoy cae dentro de
--    starts_on..ends_on y active = true.
-- ================================================================
