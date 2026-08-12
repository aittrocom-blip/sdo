-- 1. ROOMS ------------------------------------------------------------
CREATE TABLE rooms (
  id uuid primary key default gen_random_uuid(),
  sort_order int not null,
  category text not null,
  name text not null,
  description text not null,
  size_m2 numeric not null,
  size_ft2 numeric not null,
  bed text not null,
  view text not null,
  capacity_people int not null,
  features jsonb not null default '[]'::jsonb,
  photo_url text,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

ALTER TABLE rooms ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_rooms" ON rooms FOR SELECT USING (true);
CREATE POLICY "admin_all_rooms"   ON rooms FOR ALL    USING (auth.role() = 'authenticated');

-- 2. SALONS -----------------------------------------------------------
CREATE TABLE salons (
  id uuid primary key default gen_random_uuid(),
  sort_order int not null,
  name text not null,
  capacity_max int,
  capacity_note text,
  area_m2 numeric,
  floor text not null,
  montajes text not null,
  notes text,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

ALTER TABLE salons ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_salons" ON salons FOR SELECT USING (true);
CREATE POLICY "admin_all_salons"   ON salons FOR ALL    USING (auth.role() = 'authenticated');

-- 3. HOTEL_FAQ ----------------------------------------------------------
CREATE TABLE hotel_faq (
  id uuid primary key default gen_random_uuid(),
  sort_order int not null,
  category text not null,
  question text not null,
  answer text not null,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

ALTER TABLE hotel_faq ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_faq" ON hotel_faq FOR SELECT USING (true);
CREATE POLICY "admin_all_faq"   ON hotel_faq FOR ALL    USING (auth.role() = 'authenticated');
