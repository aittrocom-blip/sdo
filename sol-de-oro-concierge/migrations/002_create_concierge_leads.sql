-- 4. CONCIERGE_LEADS -----------------------------------------------------
-- Leads estructurados capturados por el AI Concierge durante la conversación (evolución
-- Fase 2: de "solo informa" a "informa + detecta intención comercial + captura lead").
-- Se inserta una sola fila por sesión, en el momento en que la conversación deriva a
-- WhatsApp — ver backend/app/api/concierge.py (_persist_lead). El widget público (anon
-- key) solo puede CREAR leads nuevos: no hay policy de SELECT/UPDATE/DELETE anónima, para
-- que un visitante nunca pueda leer o modificar el lead de otra sesión. Lectura/edición
-- quedan reservadas al rol authenticated (panel admin).
CREATE TABLE concierge_leads (
  id uuid primary key default gen_random_uuid(),
  session_id text not null,
  name text,
  email text,
  phone text,
  company text,
  lead_type text not null default 'general',
  event_type text,
  event_date text,
  guests int,
  requirements text,
  status text not null default 'new',
  source text not null default 'ai_concierge',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

ALTER TABLE concierge_leads ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_insert_leads" ON concierge_leads FOR INSERT WITH CHECK (true);
CREATE POLICY "admin_all_leads"     ON concierge_leads FOR ALL    USING (auth.role() = 'authenticated');
