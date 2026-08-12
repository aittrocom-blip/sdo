# Sol de Oro AI Concierge — Fase 1 (Prototipo) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Un backend FastAPI con un endpoint `POST /api/concierge` que responde preguntas sobre el hotel Sol de Oro usando datos reales de Supabase (nunca inventados), más un widget de chat mínimo para probarlo localmente.

**Architecture:** Una sola llamada al LLM por turno (NVIDIA Build / NIM, API OpenAI-compatible) con function-calling contra una capa de herramientas tipadas que leen de Supabase. Sesión en memoria del proceso. Sin agentes separados, sin Docker, sin integración con el sitio en producción — todo eso es de fases posteriores.

**Tech Stack:** Python 3.11+, FastAPI, uvicorn, `openai` SDK (apuntado al endpoint OpenAI-compatible de NVIDIA Build), `supabase-py` (o `httpx` directo contra PostgREST), pytest, vanilla HTML/CSS/JS para el widget.

## Global Constraints

- No convertir el sitio principal a ningún framework — el widget es JS plano, standalone en esta fase (spec, Sección "Componentes").
- No usar APIs de pago (OpenAI/Anthropic/Google Gemini) — inferencia vía NVIDIA Build (spec, decisión 1).
- No usar `service_role` de Supabase desde el backend del Concierge para lectura — usar `SUPABASE_ANON_KEY`, mismo patrón RLS que el resto del sitio (spec, nota bajo "Componentes").
- No inventar datos del hotel — toda respuesta factual debe venir de una tool que lea Supabase (spec, "Manejo de errores").
- No crear tablas de sesión/analytics en esta fase (spec, "Modelo de datos").
- No usar Docker en esta fase — correr local con `uvicorn` (spec, decisión 5).
- Sesión en memoria, no persistente (spec, decisión 6).
- Proyecto Supabase existente a reutilizar: `fjzshpilzjtfjcouzzzz` (`https://fjzshpilzjtfjcouzzzz.supabase.co`). No crear un proyecto nuevo.

---

## Nota sobre credenciales antes de empezar

Este plan asume que quien lo ejecute tiene acceso a:
1. `SUPABASE_URL` y `SUPABASE_ANON_KEY` del proyecto (públicas, ya están hardcodeadas en `admin/index.html` líneas 430-431 del sitio — reutilizar los mismos valores).
2. Un **Supabase Management API access token** (`sbp_...`) para ejecutar las migraciones DDL (`CREATE TABLE`) de las Tasks 2-3, porque PostgREST (la API pública de Supabase) no permite DDL, solo lectura/escritura de filas en tablas ya existentes. Este token es tan privilegiado como una `service_role` key — pedir confirmación explícita al usuario antes de usarlo, igual que se hizo en la sesión de auditoría.
3. Un `NVIDIA_API_KEY` de build.nvidia.com (tier gratuito) para las Tasks 8, 10 y 11. **Esto lo tiene que generar el usuario** — no existe todavía en este proyecto. Bloqueante para las Tasks 8+; las Tasks 1-7 (scaffolding + migración de datos) no lo necesitan y se pueden completar sin esperar.

---

### Task 1: Scaffolding del backend

**Files:**
- Create: `sol-de-oro-concierge/backend/requirements.txt`
- Create: `sol-de-oro-concierge/backend/.env.example`
- Create: `sol-de-oro-concierge/backend/app/__init__.py`
- Create: `sol-de-oro-concierge/backend/app/config/__init__.py`
- Create: `sol-de-oro-concierge/backend/app/config/settings.py`
- Create: `sol-de-oro-concierge/backend/app/main.py`
- Test: `sol-de-oro-concierge/backend/tests/test_health.py`

**Interfaces:**
- Produces: `app.config.settings.settings` — objeto `Settings` (pydantic `BaseSettings`) con campos `supabase_url: str`, `supabase_anon_key: str`, `nvidia_api_key: str`, `nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"`. Todas las tasks siguientes importan `from app.config.settings import settings`.
- Produces: `app.main.app` — instancia de `FastAPI`, importada por Task 10 para registrar el router.

- [ ] **Step 1: Crear `requirements.txt`**

```text
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic-settings==2.6.1
httpx==0.27.2
openai==1.54.0
pytest==8.3.3
pytest-asyncio==0.24.0
```

- [ ] **Step 2: Crear `.env.example`**

```text
SUPABASE_URL=https://fjzshpilzjtfjcouzzzz.supabase.co
SUPABASE_ANON_KEY=sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY
NVIDIA_API_KEY=
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
```

- [ ] **Step 3: Crear `app/config/settings.py`**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str
    supabase_anon_key: str
    nvidia_api_key: str
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"


settings = Settings()
```

- [ ] **Step 4: Crear `app/__init__.py` y `app/config/__init__.py` vacíos**

```python
```

- [ ] **Step 5: Crear `app/main.py` con health check**

```python
from fastapi import FastAPI

app = FastAPI(title="Sol de Oro Concierge")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

- [ ] **Step 6: Escribir el test que falla**

`tests/test_health.py`:

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 7: Instalar dependencias y correr el test**

Run (desde `sol-de-oro-concierge/backend/`):
```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
pytest tests/test_health.py -v
```
Expected: PASS (no depende de credenciales reales, `settings` solo necesita que `.env` tenga las claves de Supabase que ya son públicas; `NVIDIA_API_KEY` puede quedar vacío para este test porque `main.py` no lo usa todavía).

- [ ] **Step 8: Commit**

```bash
git add sol-de-oro-concierge/backend
git commit -m "chore: scaffold concierge backend with health check"
```

---

### Task 2: Migración DDL — crear tablas `rooms`, `salons`, `hotel_faq`

**Files:**
- Create: `sol-de-oro-concierge/migrations/001_create_rooms_salons_faq.sql`
- Create: `sol-de-oro-concierge/migrations/run_migration.py`

**Interfaces:**
- Produces: tablas Supabase `rooms`, `salons`, `hotel_faq` (schema `public`), con RLS habilitado y las mismas dos políticas que ya usa el resto del sitio (`public_read_*` para SELECT, `admin_all_*` para `authenticated`).
- Consumido por: Task 3 (INSERT de datos), Task 7 (funciones de lectura).

- [ ] **Step 1: Escribir el SQL de la migración**

`migrations/001_create_rooms_salons_faq.sql`:

```sql
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
```

- [ ] **Step 2: Escribir el script que ejecuta la migración vía Supabase Management API**

`migrations/run_migration.py`:

```python
import sys
import requests

PROJECT_REF = "fjzshpilzjtfjcouzzzz"


def run_sql(management_token: str, sql_path: str) -> None:
    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()
    resp = requests.post(
        f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query",
        headers={"Authorization": f"Bearer {management_token}", "Content-Type": "application/json"},
        json={"query": sql},
        timeout=30,
    )
    print(resp.status_code, resp.text[:2000])
    resp.raise_for_status()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python run_migration.py <management_token> <ruta_sql>")
        sys.exit(1)
    run_sql(sys.argv[1], sys.argv[2])
```

- [ ] **Step 3: PARAR — pedir confirmación antes de ejecutar**

Este paso usa un Management API token con permisos de DDL sobre el proyecto de producción. Antes de correrlo, confirmar explícitamente con el usuario (mismo criterio que se usó para crear el bucket de Storage en la sesión de auditoría). No ejecutar automáticamente sin ese visto bueno.

- [ ] **Step 4: Ejecutar la migración (tras confirmación)**

Run:
```bash
python migrations/run_migration.py <SUPABASE_MANAGEMENT_TOKEN> migrations/001_create_rooms_salons_faq.sql
```
Expected: HTTP 200, sin errores de sintaxis SQL.

- [ ] **Step 5: Verificar que las tablas existen y están vacías**

Run:
```bash
curl -s "https://fjzshpilzjtfjcouzzzz.supabase.co/rest/v1/rooms?select=id&limit=1" -H "apikey: sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY"
curl -s "https://fjzshpilzjtfjcouzzzz.supabase.co/rest/v1/salons?select=id&limit=1" -H "apikey: sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY"
curl -s "https://fjzshpilzjtfjcouzzzz.supabase.co/rest/v1/hotel_faq?select=id&limit=1" -H "apikey: sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY"
```
Expected: cada uno devuelve `[]` (200 OK, tabla vacía) — si devuelve 404 o error de "relation does not exist", la migración falló.

- [ ] **Step 6: Commit**

```bash
git add sol-de-oro-concierge/migrations
git commit -m "feat: create rooms, salons, hotel_faq tables in Supabase"
```

---

### Task 3: Migrar datos de `rooms` (9 filas, desde `habitaciones.html`)

**Files:**
- Create: `sol-de-oro-concierge/migrations/seed_rooms.py`

**Interfaces:**
- Consumes: tabla `rooms` (Task 2).
- Produces: 9 filas en `rooms`, usadas por `get_rooms()` en Task 7.

- [ ] **Step 1: Escribir el script con los datos reales (transcritos de `habitaciones.html` líneas 232-240, sitio principal)**

`migrations/seed_rooms.py`:

```python
import requests

SUPA_URL = "https://fjzshpilzjtfjcouzzzz.supabase.co"
SUPA_KEY = "sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY"
SITE = "https://soldeoro.com.pe"

ROOMS = [
    dict(sort_order=1, category="01 · Esencial", name="Standard Room",
         description="Esta habitación cuenta con una cama matrimonial, baño privado con bañera y secador de pelo, aire acondicionado, TV de pantalla plana con cable, entrada privada, paredes insonorizadas y armario.",
         size_m2=25, size_ft2=269, bed="1 Cama matrimonial", view="Exterior", capacity_people=2,
         features=["Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con bañera", "Smart TV cable"],
         photo_url=f"{SITE}/images/Habitaciones/FOTOS-WEB-SOL-DE-ORO_11zon-1.jpg"),
    dict(sort_order=2, category="02 · Esencial", name="Standard Room Twin",
         description="Esta habitación cuenta con dos camas twin (100×200 cm), baño privado con bañera y secador de pelo, aire acondicionado, TV de pantalla plana, entrada privada, paredes insonorizadas y armario.",
         size_m2=25, size_ft2=269, bed="2 Twin (100×200 cm)", view="Exterior", capacity_people=2,
         features=["Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con bañera", "Smart TV cable"],
         photo_url=f"{SITE}/images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-1_2_11zon.jpg"),
    dict(sort_order=3, category="03 · Confort", name="Superior King Room",
         description="La habitación cuenta con una cama king, aire acondicionado, entrada privada y baño privado con ducha y secador de pelo. Armario, caja fuerte y TV de pantalla plana con cable.",
         size_m2=27, size_ft2=291, bed="1 Cama King", view="Miraflores", capacity_people=2,
         features=["Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con ducha", "Smart TV cable"],
         photo_url=f"{SITE}/images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-2_11zon.jpg"),
    dict(sort_order=4, category="04 · Confort", name="Superior Twin Room",
         description="La habitación cuenta con dos camas queen, aire acondicionado, entrada privada y baño privado con ducha y secador de pelo. Armario, caja fuerte y TV de pantalla plana con cable.",
         size_m2=27, size_ft2=291, bed="2 Camas Queen", view="Miraflores", capacity_people=2,
         features=["Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con ducha", "Smart TV cable"],
         photo_url=f"{SITE}/images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-3_11zon.jpg"),
    dict(sort_order=5, category="05 · Suite", name="Junior Suite",
         description="La habitación cuenta con cama king, aire acondicionado, armario, caja fuerte, TV de pantalla plana con canales y baño privado con ducha y secador de pelo.",
         size_m2=40, size_ft2=431, bed="1 Cama King", view="Miraflores", capacity_people=3,
         features=["Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con ducha", "Smart TV cable"],
         photo_url=f"{SITE}/images/Habitaciones/JUNIOR-SUITE_11zon.jpg"),
    dict(sort_order=6, category="06 · Suite", name="Junior Suite Twin",
         description="La habitación cuenta con dos camas queen, aire acondicionado, armario, caja fuerte, TV de pantalla plana con canales y baño privado con ducha y secador de pelo.",
         size_m2=40, size_ft2=431, bed="2 Camas Queen", view="Miraflores", capacity_people=3,
         features=["Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con ducha", "Smart TV cable"],
         photo_url=f"{SITE}/images/Habitaciones/JUNIOR-SUITE-TWIN_11zon.jpg"),
    dict(sort_order=7, category="07 · Premium", name="Executive Suite",
         description="La habitación cuenta con una cama king, aire acondicionado, armario, caja fuerte y TV de pantalla plana con cable. Cuenta con sala interna, baño privado con ducha y secador de pelo.",
         size_m2=80, size_ft2=861, bed="1 Cama King", view="Miraflores · piso alto", capacity_people=2,
         features=["Sala interna", "Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con ducha", "Smart TV cable"],
         photo_url=f"{SITE}/images/Habitaciones/FOTOS-WEB-SOL-DE-ORO_11zon.jpg"),
    dict(sort_order=8, category="08 · Premium", name="Suite Deluxe",
         description="La habitación cuenta con dos camas queen, aire acondicionado, jacuzzi interno, armario, caja fuerte, TV de pantalla plana con canales y baño privado con ducha y secador de pelo.",
         size_m2=80, size_ft2=861, bed="2 Camas Queen", view="Miraflores · piso alto", capacity_people=2,
         features=["Jacuzzi interno", "Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con ducha", "Smart TV cable"],
         photo_url=f"{SITE}/images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-5_11zon.jpg"),
    dict(sort_order=9, category="09 · Insignia", name="Grand Deluxe Suite",
         description="La habitación cuenta con una cama king, área de estar, aire acondicionado, armario, caja fuerte y TV de pantalla plana con cable. Cuenta con jacuzzi interno, sala interna, baño privado con ducha y secador de pelo.",
         size_m2=80, size_ft2=861, bed="1 Cama King", view="Miraflores · piso alto", capacity_people=2,
         features=["Jacuzzi interno", "Sala de estar", "Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Smart TV cable"],
         photo_url=f"{SITE}/images/Habitaciones/FOTOS-WEB-SOL-DE-ORO-3_11zon-1.jpg"),
]


def main() -> None:
    resp = requests.post(
        f"{SUPA_URL}/rest/v1/rooms",
        headers={"apikey": SUPA_KEY, "Content-Type": "application/json", "Prefer": "return=representation"},
        json=ROOMS,
        timeout=30,
    )
    print(resp.status_code, len(resp.json()) if resp.status_code == 201 else resp.text[:500])
    resp.raise_for_status()


if __name__ == "__main__":
    main()
```

**Nota:** este POST usa solo `SUPA_KEY` (anon), no requiere token de management — pero la política `admin_all_rooms` exige `authenticated`, así que en realidad hace falta autenticar primero como el usuario admin (mismo patrón usado en toda la sesión de auditoría: `POST /auth/v1/token?grant_type=password` con las credenciales del panel admin, y usar el `access_token` resultante como `Authorization: Bearer` además del `apikey`). Ajustar el script para incluir ese login antes de este POST — replicar exactamente el patrón de `update_restaurants.py` usado en la sesión previa de este proyecto.

- [ ] **Step 2: Ejecutar y verificar**

Run:
```bash
python migrations/seed_rooms.py
curl -s "https://fjzshpilzjtfjcouzzzz.supabase.co/rest/v1/rooms?select=name&order=sort_order" -H "apikey: sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY"
```
Expected: 9 nombres de habitación, en el orden correcto (Standard Room → Grand Deluxe Suite).

- [ ] **Step 3: Commit**

```bash
git add sol-de-oro-concierge/migrations/seed_rooms.py
git commit -m "feat: seed rooms table with 9 room types from habitaciones.html"
```

---

### Task 4: Migrar datos de `salons` (9 filas, desde la tabla de capacidades de `eventos.html`)

**Files:**
- Create: `sol-de-oro-concierge/migrations/seed_salons.py`

**Interfaces:**
- Consumes: tabla `salons` (Task 2).
- Produces: 9 filas en `salons`, usadas por `get_salons()` en Task 7.

- [ ] **Step 1: Escribir el script (datos transcritos de `eventos.html` tabla `#capacidad`, líneas 376-384)**

`migrations/seed_salons.py`:

```python
import requests

SUPA_URL = "https://fjzshpilzjtfjcouzzzz.supabase.co"
SUPA_KEY = "sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY"

SALONS = [
    dict(sort_order=1, name="Ejecutivo I", capacity_max=60, capacity_note=None, area_m2=72,
         floor="1", montajes="Auditorio · Escuela · Banquete", notes="Reuniones privadas"),
    dict(sort_order=2, name="Ejecutivo II", capacity_max=80, capacity_note=None, area_m2=160,
         floor="1", montajes="Auditorio · Escuela · Banquete", notes="Talleres ejecutivos"),
    dict(sort_order=3, name="Ejecutivo III", capacity_max=120, capacity_note=None, area_m2=250,
         floor="1", montajes="Auditorio · Escuela · Banquete · Cóctel", notes="Multi-formato"),
    dict(sort_order=4, name="Empresarial I", capacity_max=100, capacity_note=None, area_m2=132,
         floor="2", montajes="Auditorio · Escuela · Banquete · Cóctel", notes="Conferencias"),
    dict(sort_order=5, name="Empresarial II", capacity_max=100, capacity_note=None, area_m2=128,
         floor="2", montajes="Auditorio · Escuela · Banquete · Cóctel", notes="Conferencias"),
    dict(sort_order=6, name="Empresarial III", capacity_max=150, capacity_note=None, area_m2=170,
         floor="2", montajes="Auditorio · Escuela · Banquete · Cóctel", notes="Banquetes corporativos"),
    dict(sort_order=7, name="Empresarial Completo", capacity_max=500, capacity_note=None, area_m2=430,
         floor="2", montajes="Auditorio · Banquete · Cóctel · Modular", notes="Auditorio · divisible en 3"),
    dict(sort_order=8, name="Salón Sol de Oro", capacity_max=100, capacity_note="100 (cóctel) / 80 (banquete)", area_m2=126,
         floor="12", montajes="Cóctel 100 · Banquete 80 · Auditorio 80 · Escuela 50", notes="Terraza panorámica"),
    dict(sort_order=9, name="Centro de Convenciones", capacity_max=None, capacity_note="Variable según montaje", area_m2=230,
         floor="2", montajes="Ferias · Exhibiciones · Coffee · Cóctel", notes="Indoor + outdoor"),
]


def main() -> None:
    resp = requests.post(
        f"{SUPA_URL}/rest/v1/salons",
        headers={"apikey": SUPA_KEY, "Content-Type": "application/json", "Prefer": "return=representation"},
        json=SALONS,
        timeout=30,
    )
    print(resp.status_code, len(resp.json()) if resp.status_code == 201 else resp.text[:500])
    resp.raise_for_status()


if __name__ == "__main__":
    main()
```

Igual que en Task 3: agregar el login del admin (`/auth/v1/token?grant_type=password`) antes del POST, ya que la política `admin_all_salons` requiere `authenticated`.

- [ ] **Step 2: Ejecutar y verificar**

Run:
```bash
python migrations/seed_salons.py
curl -s "https://fjzshpilzjtfjcouzzzz.supabase.co/rest/v1/salons?select=name,capacity_max&order=sort_order" -H "apikey: sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY"
```
Expected: 9 salones, "Empresarial Completo" con `capacity_max: 500`, "Centro de Convenciones" con `capacity_max: null`.

- [ ] **Step 3: Commit**

```bash
git add sol-de-oro-concierge/migrations/seed_salons.py
git commit -m "feat: seed salons table with 9 event spaces from eventos.html"
```

---

### Task 5: Migrar datos de `hotel_faq` (22 filas, desde `faq.html`)

**Files:**
- Create: `sol-de-oro-concierge/migrations/seed_faq.py`

**Interfaces:**
- Consumes: tabla `hotel_faq` (Task 2).
- Produces: 22 filas en `hotel_faq`, usadas por `get_faq()` en Task 7.

- [ ] **Step 1: Escribir el script (contenido transcrito completo de `faq.html`, sin resumir ni parafrasear)**

`migrations/seed_faq.py`:

```python
import requests

SUPA_URL = "https://fjzshpilzjtfjcouzzzz.supabase.co"
SUPA_KEY = "sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY"

FAQ = [
    # Llegada y estadía
    dict(sort_order=1, category="Llegada y estadía", question="¿A qué hora puedo hacer check-in y check-out?",
         answer="Check-in: 3:00 p.m. Check-out: 12:00 p.m. Si necesitas early check-in o late check-out, escríbenos con anticipación y lo coordinamos sujeto a disponibilidad."),
    dict(sort_order=2, category="Llegada y estadía", question="¿Cómo llego al hotel desde el Aeropuerto Jorge Chávez?",
         answer="El Aeropuerto Internacional Jorge Chávez está a aproximadamente 20 km (35 a 45 minutos en automóvil según el tráfico) de nuestro hotel en Ca. San Martín 305, Miraflores. Opciones recomendadas: Taxi oficial del aeropuerto (counter dentro del terminal, tarifa fija). App de viaje (Uber, Cabify, Didi, InDriver) en zona habilitada de salida. Traslado privado del hotel — coordinable con anticipación al reservas@soldeoro.pe."),
    dict(sort_order=3, category="Llegada y estadía", question="¿Tienen estacionamiento?",
         answer="Sí. Tres niveles de estacionamiento con capacidad para 62 vehículos, incluyendo espacios para personas con discapacidad y módulos para bicicletas o motos. El servicio está incluido para huéspedes."),
    dict(sort_order=4, category="Llegada y estadía", question="¿Qué tarjetas aceptan?",
         answer="Aceptamos: American Express, Diners Club, Mastercard y Visa. El hotel se reserva el derecho de aceptar tarjetas únicamente cuando son portadas por su titular."),
    dict(sort_order=5, category="Llegada y estadía", question="¿Qué pasa si necesito cancelar o salir antes?",
         answer="Aplica una política estándar de cancelación. Para casos específicos o salidas anticipadas, comunícate con Recepción al anexo 2199 o llámanos al +51 (1) 610-7000."),
    # Habitaciones
    dict(sort_order=6, category="Habitaciones", question="¿Cuántos tipos de habitación hay?",
         answer="Tenemos 9 categorías: Standard Room — 25 m², 2 personas, cama matrimonial. Standard Room Twin — 25 m², 2 personas, dos camas individuales. Superior King Room — 27 m², 2 personas, cama king. Superior Twin Room — 27 m², 2 personas, dos camas queen. Junior Suite — 40 m², 3 personas, cama king. Junior Suite Twin — 40 m², 3 personas, dos camas queen. Executive Suite — 80 m², 2 personas, cama king + sala. Suite Deluxe — 80 m², 2 personas, dos camas queen + jacuzzi. Grand Deluxe Suite — 80 m², 2 personas, cama king + sala + jacuzzi."),
    dict(sort_order=7, category="Habitaciones", question="¿Hay Wi-Fi y es gratis?",
         answer="Sí. Wi-Fi gratuito en todo el hotel: habitaciones, áreas comunes, terraza, spa y gimnasio."),
    dict(sort_order=8, category="Habitaciones", question="¿Las habitaciones tienen aire acondicionado?",
         answer="Sí. Todas las habitaciones cuentan con aire acondicionado independiente."),
    dict(sort_order=9, category="Habitaciones", question="¿Hay caja de seguridad?",
         answer="Sí. Todas las habitaciones tienen caja fuerte tamaño laptop. El servicio es sin cargo. El hotel no se responsabiliza por objetos de valor que se dejen fuera de la caja de seguridad."),
    dict(sort_order=10, category="Habitaciones", question="¿Disponen de cunas para bebés?",
         answer="Sí. Disponemos de cunas sin cargo, a solicitud al momento de reservar o al hacer check-in."),
    # Mascotas, fumadores y reglas
    dict(sort_order=11, category="Mascotas, fumadores y reglas", question="¿Puedo llevar mi mascota?",
         answer="Sí, con condiciones: Solo se permiten perros guía dentro de las áreas comunes del hotel. Se permite un perro de máximo 6 kg en la habitación. Para más detalles, consulta con reservas@soldeoro.pe antes de tu llegada."),
    dict(sort_order=12, category="Mascotas, fumadores y reglas", question="¿Se puede fumar dentro del hotel?",
         answer="No. Todas las habitaciones e instalaciones son 100% libres de humo. Por incumplimiento se aplica una penalidad de S/. 500.00."),
    # Servicios
    dict(sort_order=13, category="Servicios", question="¿Qué servicios incluye mi estadía?",
         answer="Wi-Fi gratuito en todo el hotel. Estacionamiento. Caja fuerte en habitación. Acceso a piscina al aire libre. Acceso a gimnasio y spa. Servicio a habitación (room service). Servicio de lavandería (con cargo según consumo)."),
    dict(sort_order=14, category="Servicios", question="¿A qué hora se sirve el desayuno?",
         answer="Desayuno buffet en el Restaurante Murano (primer piso): Lunes a viernes: 7:00 a.m. – 10:00 a.m. Sábados, domingos y feriados: 7:00 a.m. – 11:00 a.m."),
    dict(sort_order=15, category="Servicios", question="¿Tienen restaurante? ¿Está abierto al público?",
         answer="Sí. Restaurante Murano, cocina peruana e internacional, abierto al público: Atención general: 7:00 a.m. – 11:00 p.m. todos los días. Almuerzo ejecutivo: lunes a sábado, 12:00 p.m. – 3:00 p.m. Bar Murano: todos los días, 7:00 a.m. – 11:00 p.m."),
    dict(sort_order=16, category="Servicios", question="¿Hay room service?",
         answer="Sí, servicio a la habitación disponible en horarios establecidos. Consulta el menú en habitación o llama a Recepción para coordinar."),
    dict(sort_order=17, category="Servicios", question="¿Tienen piscina, gimnasio y spa?",
         answer="Sí. Disponemos de: Piscina al aire libre. Gimnasio de acceso libre para huéspedes. Spa con tratamientos disponibles. Para reservar tratamientos consulta en Recepción."),
    # Eventos y reuniones
    dict(sort_order=18, category="Eventos y reuniones", question="¿Tienen salones para eventos?",
         answer="Sí. Cuatro grupos de espacios distribuidos en tres pisos: Salones Ejecutivos I, II, III — pisos 1 y 2, capacidad 60 a 120 personas. Salones Empresariales I, II, III — piso 2, hasta 500 personas unidos. Salón Sol de Oro — piso 12 con terraza panorámica, hasta 100 personas en cóctel. Centro de Convenciones — segundo piso, capacidad variable según montaje."),
    dict(sort_order=19, category="Eventos y reuniones", question="¿Cómo cotizo un evento?",
         answer="Escribe a comercial@soldeoro.pe, llama al +51 988 861 380 o escríbenos por WhatsApp (https://wa.link/dc0dft). Te respondemos con cotización personalizada en menos de 24 horas hábiles."),
    # Información para huéspedes internacionales
    dict(sort_order=20, category="Información para huéspedes internacionales", question="¿Cuál es el voltaje en Perú?",
         answer="220 V · 60 Hz · Tomas tipo A/B/C. Si tu equipo es 110 V (común en Estados Unidos y partes de México), necesitarás un convertidor o adaptador. Si vienes de Europa (230 V), basta con un adaptador de pin."),
    dict(sort_order=21, category="Información para huéspedes internacionales", question="¿Qué moneda se usa en Perú?",
         answer="El Sol peruano (PEN, S/). Aceptamos las principales tarjetas internacionales (Visa, Mastercard, Amex, Diners). Cajeros automáticos abundantes en Miraflores."),
    dict(sort_order=22, category="Información para huéspedes internacionales", question="¿Qué idiomas se hablan en el hotel?",
         answer="Atendemos en español. Nuestro equipo de Recepción puede asistirte también en otros idiomas — consulta al momento de tu reserva."),
]


def main() -> None:
    resp = requests.post(
        f"{SUPA_URL}/rest/v1/hotel_faq",
        headers={"apikey": SUPA_KEY, "Content-Type": "application/json", "Prefer": "return=representation"},
        json=FAQ,
        timeout=30,
    )
    print(resp.status_code, len(resp.json()) if resp.status_code == 201 else resp.text[:500])
    resp.raise_for_status()


if __name__ == "__main__":
    main()
```

Igual que Tasks 3-4: agregar login admin antes del POST (política `authenticated`).

- [ ] **Step 2: Ejecutar y verificar**

Run:
```bash
python migrations/seed_faq.py
curl -s "https://fjzshpilzjtfjcouzzzz.supabase.co/rest/v1/hotel_faq?select=category&order=sort_order" -H "apikey: sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY" | python -c "import sys,json; print(len(json.load(sys.stdin)))"
```
Expected: `22`.

- [ ] **Step 3: Commit**

```bash
git add sol-de-oro-concierge/migrations/seed_faq.py
git commit -m "feat: seed hotel_faq table with 22 Q&A from faq.html"
```

---

### Task 6: Reemplazar contenido de `le_experiences` con las 19 tarjetas de "Explorar Lima"

**Files:**
- Create: `sol-de-oro-concierge/migrations/seed_experiences.py`
- Modify: `admin/index.html` (constante `CAT_LABELS`, alrededor de la línea donde se define `const CAT_LABELS = { gastronomy:'Gastronomía', ... }`)

**Interfaces:**
- Consumes: tabla `le_experiences` (ya existente).
- Produces: 19 filas activas en `le_experiences`, usadas por `get_nearby()` en Task 7. Deja el admin coherente con las categorías nuevas.

- [ ] **Step 1: Escribir el script — borra las filas huérfanas actuales e inserta las 19 reales**

`migrations/seed_experiences.py`:

```python
import requests

SUPA_URL = "https://fjzshpilzjtfjcouzzzz.supabase.co"
SUPA_KEY = "sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY"
BUCKET = f"{SUPA_URL}/storage/v1/object/public/experiences"
SITE = "https://soldeoro.com.pe"


def login() -> str:
    r = requests.post(
        f"{SUPA_URL}/auth/v1/token?grant_type=password",
        headers={"apikey": SUPA_KEY, "Content-Type": "application/json"},
        json={"email": "aittro.com@gmail.com", "password": "1234567890"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"]


EXPERIENCES = [
    # cat=hotel
    dict(sort_order=1, mode="modern", cat="hotel", title="Piscina temperada", zone="En el hotel",
         excerpt="Piscina temperada en la terraza del piso 14, climatizada todo el año con vista a Miraflores.",
         tag="En el hotel · Piso 14", photo_url=f"{SITE}/images/Rooftop/PISCINA-WEB.webp",
         maps_url="https://maps.google.com/?q=Sol+de+Oro+Hotel+Suites+Miraflores"),
    dict(sort_order=2, mode="modern", cat="hotel", title="Gimnasio 24h", zone="En el hotel",
         excerpt="Equipamiento Technogym, peso libre y cardio con vista al Pacífico, abierto las 24 horas.",
         tag="En el hotel · Gimnasio", photo_url=f"{SITE}/images/Gimnasio/4_4_11zon.jpg",
         maps_url="https://maps.google.com/?q=Sol+de+Oro+Hotel+Suites+Miraflores"),
    dict(sort_order=3, mode="modern", cat="hotel", title="Spa & Masajes", zone="En el hotel",
         excerpt="Rituales con tradición peruana, sauna seco, hidromasaje y cabinas de pareja. Reserva con anticipación.",
         tag="En el hotel · Spa", photo_url=f"{SITE}/images/Spa/MG_1800_ED_11zon-scaled.jpg",
         maps_url="https://maps.google.com/?q=Sol+de+Oro+Hotel+Suites+Miraflores"),
    # cat=shopping
    dict(sort_order=4, mode="modern", cat="shopping", title="Larcomar", zone="Miraflores",
         excerpt="Centro comercial sobre los acantilados del Pacífico, con tiendas, entretenimiento y vistas al mar.",
         tag="10 min · Compras", photo_url=f"{BUCKET}/explore/larcomar_v2.jpg",
         maps_url="https://maps.google.com/?q=Larcomar+Miraflores+Lima"),
    dict(sort_order=5, mode="modern", cat="shopping", title="Parque Kennedy", zone="Miraflores",
         excerpt="El corazón de Miraflores, rodeado de cafés, tiendas, galerías y vida urbana.",
         tag="8 min · Centro", photo_url=f"{BUCKET}/explore/parque_kennedy_v2.jpg",
         maps_url="https://maps.google.com/?q=Parque+Kennedy+Miraflores+Lima"),
    dict(sort_order=6, mode="modern", cat="shopping", title="Av. Larco", zone="Miraflores",
         excerpt="Una de las principales avenidas comerciales de Miraflores, conecta el hotel con Kennedy y Larcomar.",
         tag="2 min · Shopping", photo_url=f"{BUCKET}/explore/av_larco.jpg",
         maps_url="https://maps.google.com/?q=Avenida+Larco+Miraflores+Lima"),
    dict(sort_order=7, mode="modern", cat="shopping", title="Mercado Indio", zone="Miraflores",
         excerpt="Mercado de artesanía peruana, con textiles, cerámica y souvenirs tradicionales.",
         tag="20 min · Artesanía", photo_url=f"{BUCKET}/explore/mercado_indio.jpg",
         maps_url="https://maps.google.com/?q=Mercado+Indio+Miraflores+Lima"),
    # cat=coast
    dict(sort_order=8, mode="modern", cat="coast", title="Malecón de Miraflores", zone="Miraflores",
         excerpt="Paseo sobre los acantilados con vistas al Pacífico, ideal para caminar, correr o contemplar el mar.",
         tag="10 min · Caminata", photo_url="https://images.unsplash.com/photo-1531968455001-5c5272a41129?auto=format&fit=crop&w=900&q=80",
         maps_url="https://maps.google.com/?q=Malecon+de+Miraflores+Lima"),
    dict(sort_order=9, mode="modern", cat="coast", title="Parque del Amor", zone="Miraflores",
         excerpt="Parque emblemático del malecón, conocido por su escultura, mosaicos y vistas al Pacífico.",
         tag="20 min · Atardecer", photo_url="https://images.unsplash.com/photo-1505142468610-359e7d316be0?auto=format&fit=crop&w=900&q=80",
         maps_url="https://maps.google.com/?q=Parque+del+Amor+Miraflores+Lima"),
    dict(sort_order=10, mode="modern", cat="coast", title="Faro de la Marina", zone="Miraflores",
         excerpt="Faro histórico frente al Pacífico, uno de los puntos más fotogénicos del malecón.",
         tag="20 min · Mirador", photo_url=f"{BUCKET}/explore/faro_marina.jpg",
         maps_url="https://maps.google.com/?q=Faro+La+Marina+Miraflores+Lima"),
    dict(sort_order=11, mode="modern", cat="coast", title="Parque María Reiche", zone="Miraflores",
         excerpt="Parque costero inspirado en las Líneas de Nazca, ideal para continuar el paseo por el malecón.",
         tag="25 min · Arte", photo_url=f"{BUCKET}/explore/parque_reiche.jpg",
         maps_url="https://maps.google.com/?q=Parque+Maria+Reiche+Miraflores+Lima"),
    dict(sort_order=12, mode="modern", cat="coast", title="Costa Verde", zone="Miraflores",
         excerpt="Carretera costera con playas, surf y vista a los acantilados de Lima.",
         tag="12 min · Playas", photo_url="https://images.unsplash.com/photo-1535007813616-79dc02ba4021?auto=format&fit=crop&w=900&q=80",
         maps_url="https://maps.google.com/?q=Costa+Verde+Lima"),
    dict(sort_order=13, mode="modern", cat="coast", title="Playa Waikiki", zone="Miraflores",
         excerpt="Una de las playas clásicas de Miraflores, vinculada al surf y a la Costa Verde.",
         tag="20 min · Surf", photo_url=f"{BUCKET}/explore/playa_waikiki.jpg",
         maps_url="https://maps.google.com/?q=Playa+Waikiki+Miraflores+Lima"),
    dict(sort_order=14, mode="modern", cat="coast", title="Playa Makaha", zone="Miraflores",
         excerpt="Playa de Miraflores frecuentada por surfistas, un buen punto para vivir la Costa Verde.",
         tag="20 min · Surf", photo_url=f"{BUCKET}/explore/playa_makaha.jpg",
         maps_url="https://maps.google.com/?q=Playa+Makaha+Miraflores+Lima"),
    # cat=paseos
    dict(sort_order=15, mode="modern", cat="paseos", title="Barranco", zone="Barranco",
         excerpt="Distrito bohemio de Lima, conocido por su arte urbano, galerías y vida cultural.",
         tag="12 min · Paseo", photo_url=f"{BUCKET}/explore/barranco_v2.jpg",
         maps_url="https://maps.google.com/?q=Barranco+Lima"),
    dict(sort_order=16, mode="modern", cat="paseos", title="Puente de los Suspiros", zone="Barranco",
         excerpt="Uno de los lugares más emblemáticos de Barranco, punto clásico para recorrer el distrito.",
         tag="20 min · Mirador", photo_url=f"{BUCKET}/explore/puente_suspiros.jpg",
         maps_url="https://maps.google.com/?q=Puente+de+los+Suspiros+Barranco+Lima"),
    # cat=business
    dict(sort_order=17, mode="business", cat="business", title="Centro Empresarial Miraflores", zone="Miraflores",
         excerpt="Zona de oficinas, reuniones y servicios corporativos en el entorno empresarial de Miraflores.",
         tag="12 min · Negocios", photo_url=f"{BUCKET}/explore/centro_empresarial_v2.jpg",
         maps_url="https://maps.google.com/?q=Miraflores+Lima+centro+empresarial"),
    dict(sort_order=18, mode="business", cat="business", title="Centro Financiero San Isidro", zone="San Isidro",
         excerpt="Principal zona corporativa y financiera de Lima, con oficinas, bancos y servicios profesionales.",
         tag="35 min · Finanzas", photo_url=f"{BUCKET}/explore/centro_financiero.jpg",
         maps_url="https://maps.google.com/?q=San+Isidro+Lima+centro+financiero"),
    dict(sort_order=19, mode="business", cat="business", title="Coworking · Reuniones", zone="Miraflores",
         excerpt="Espacios de trabajo y salas de reuniones para huéspedes que necesitan trabajar o extender su jornada profesional.",
         tag="12 min · Reuniones", photo_url=f"{BUCKET}/explore/coworking.jpg",
         maps_url="https://maps.google.com/?q=coworking+Miraflores+Lima"),
]


def main() -> None:
    token = login()
    headers = {"apikey": SUPA_KEY, "Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Borrar el contenido huérfano actual (~40 filas que ninguna página pública usa)
    del_resp = requests.delete(f"{SUPA_URL}/rest/v1/le_experiences?id=neq.00000000-0000-0000-0000-000000000000", headers=headers, timeout=30)
    print("DELETE", del_resp.status_code)
    del_resp.raise_for_status()

    ins_resp = requests.post(
        f"{SUPA_URL}/rest/v1/le_experiences",
        headers={**headers, "Prefer": "return=representation"},
        json=EXPERIENCES,
        timeout=30,
    )
    print("INSERT", ins_resp.status_code, len(ins_resp.json()) if ins_resp.status_code == 201 else ins_resp.text[:500])
    ins_resp.raise_for_status()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Ejecutar y verificar**

Run:
```bash
python migrations/seed_experiences.py
curl -s "https://fjzshpilzjtfjcouzzzz.supabase.co/rest/v1/le_experiences?select=cat&active=eq.true" -H "apikey: sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY" | python -c "import sys,json; d=json.load(sys.stdin); print(len(d))"
```
Expected: `19`.

- [ ] **Step 3: Actualizar `CAT_LABELS` en el admin para que el formulario de "Experiencias" ofrezca las categorías nuevas**

En `admin/index.html`, buscar la línea:
```javascript
const CAT_LABELS = { gastronomy:'Gastronomía', culture:'Cultura', shopping:'Compras', wellness:'Wellness', nightlife:'Nocturno', hidden:'Lima oculta' };
```
Reemplazar por:
```javascript
const CAT_LABELS = { hotel:'En el hotel', shopping:'Compras · Ocio', coast:'Costa', paseos:'Paseos', business:'Empresarial' };
```

- [ ] **Step 4: Verificar en el admin que el tab "Experiencias" muestra las 19 filas con las categorías correctas**

Abrir `admin/index.html` local (servidor ya usado en sesiones previas: `python -m http.server 8000` desde la raíz del sitio), login, tab "Experiencias" → confirmar 19 filas, columna "Categoría" mostrando "En el hotel / Compras · Ocio / Costa / Paseos / Empresarial" en vez de los valores viejos.

- [ ] **Step 5: Commit**

```bash
git add sol-de-oro-concierge/migrations/seed_experiences.py admin/index.html
git commit -m "feat: replace orphaned le_experiences content with the 19 Explorar Lima cards"
```

---

### Task 7: Capa de herramientas de lectura (`app/tools/supabase.py`)

**Files:**
- Create: `sol-de-oro-concierge/backend/app/tools/__init__.py`
- Create: `sol-de-oro-concierge/backend/app/tools/supabase.py`
- Test: `sol-de-oro-concierge/backend/tests/test_tools_supabase.py`

**Interfaces:**
- Consumes: tablas `rooms`, `salons`, `hotel_faq`, `le_restaurants`, `le_cultural`, `le_experiences`, `offers` (Tasks 2-6 + tablas ya existentes).
- Produces: funciones síncronas, todas devuelven `list[dict]`:
  - `get_rooms() -> list[dict]`
  - `get_salons(min_pax: int | None = None) -> list[dict]`
  - `get_faq(topic: str | None = None) -> list[dict]`
  - `get_nearby(cat: str | None = None) -> list[dict]`
  - `get_restaurants() -> list[dict]`
  - `get_cultural() -> list[dict]`
  - `get_offers() -> list[dict]`

  Estas 7 funciones son las "tools" que Task 8 (cliente NVIDIA) expone al modelo por function-calling, y las que Task 10 (endpoint) invoca directamente.

- [ ] **Step 1: Escribir el test (usa datos reales de Supabase — test de integración, no mock, porque el objetivo es validar contra los datos que se acaban de migrar)**

`tests/test_tools_supabase.py`:

```python
from app.tools.supabase import get_rooms, get_salons, get_faq, get_nearby, get_restaurants, get_cultural, get_offers


def test_get_rooms_returns_nine_rooms_sorted():
    rooms = get_rooms()
    assert len(rooms) == 9
    assert rooms[0]["name"] == "Standard Room"
    assert rooms[-1]["name"] == "Grand Deluxe Suite"


def test_get_salons_filters_by_min_pax():
    all_salons = get_salons()
    assert len(all_salons) == 9
    big_salons = get_salons(min_pax=150)
    names = {s["name"] for s in big_salons}
    assert "Empresarial Completo" in names
    assert "Ejecutivo I" not in names


def test_get_faq_filters_by_topic():
    all_faq = get_faq()
    assert len(all_faq) == 22
    pet_faq = get_faq(topic="mascota")
    assert any("mascota" in f["question"].lower() for f in pet_faq)


def test_get_nearby_filters_by_category():
    all_nearby = get_nearby()
    assert len(all_nearby) == 19
    coast = get_nearby(cat="coast")
    assert len(coast) == 7
    assert all(item["cat"] == "coast" for item in coast)


def test_get_restaurants_returns_active_only():
    restaurants = get_restaurants()
    assert len(restaurants) >= 6
    assert all(r["active"] for r in restaurants)


def test_get_cultural_returns_rows():
    cultural = get_cultural()
    assert len(cultural) >= 1


def test_get_offers_returns_list():
    offers = get_offers()
    assert isinstance(offers, list)
```

- [ ] **Step 2: Correr el test para verificar que falla**

Run: `pytest tests/test_tools_supabase.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'app.tools.supabase'`.

- [ ] **Step 3: Implementar `app/tools/__init__.py` (vacío) y `app/tools/supabase.py`**

```python
```

`app/tools/supabase.py`:

```python
import httpx

from app.config.settings import settings

_HEADERS = {"apikey": settings.supabase_anon_key}


def _get(path: str, params: dict) -> list[dict]:
    resp = httpx.get(f"{settings.supabase_url}/rest/v1/{path}", headers=_HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_rooms() -> list[dict]:
    return _get("rooms", {"select": "*", "active": "eq.true", "order": "sort_order"})


def get_salons(min_pax: int | None = None) -> list[dict]:
    params = {"select": "*", "active": "eq.true", "order": "sort_order"}
    if min_pax is not None:
        params["capacity_max"] = f"gte.{min_pax}"
    return _get("salons", params)


def get_faq(topic: str | None = None) -> list[dict]:
    params = {"select": "*", "active": "eq.true", "order": "sort_order"}
    if topic:
        params["or"] = f"(question.ilike.*{topic}*,answer.ilike.*{topic}*)"
    return _get("hotel_faq", params)


def get_nearby(cat: str | None = None) -> list[dict]:
    params = {"select": "*", "active": "eq.true", "order": "sort_order"}
    if cat:
        params["cat"] = f"eq.{cat}"
    return _get("le_experiences", params)


def get_restaurants() -> list[dict]:
    return _get("le_restaurants", {"select": "*", "active": "eq.true", "order": "sort_order"})


def get_cultural() -> list[dict]:
    return _get("le_cultural", {"select": "*", "active": "eq.true", "order": "sort_order"})


def get_offers() -> list[dict]:
    return _get("offers", {"select": "*", "active": "eq.true", "order": "sort_order"})
```

- [ ] **Step 4: Correr el test de nuevo**

Run: `pytest tests/test_tools_supabase.py -v`
Expected: PASS (requiere que Tasks 2-6 ya se hayan ejecutado contra Supabase — si alguna migración no corrió, el test correspondiente falla y señala cuál).

- [ ] **Step 5: Commit**

```bash
git add sol-de-oro-concierge/backend/app/tools sol-de-oro-concierge/backend/tests/test_tools_supabase.py
git commit -m "feat: add typed Supabase read tools for rooms, salons, faq, nearby, restaurants, cultural, offers"
```

---

### Task 8: Cliente NVIDIA Build (`app/llm/nvidia_client.py`)

**Files:**
- Create: `sol-de-oro-concierge/backend/app/llm/__init__.py`
- Create: `sol-de-oro-concierge/backend/app/llm/nvidia_client.py`
- Test: `sol-de-oro-concierge/backend/tests/test_nvidia_client.py`

**Interfaces:**
- Consumes: `settings.nvidia_api_key`, `settings.nvidia_base_url` (Task 1).
- Produces: `chat(messages: list[dict], tools: list[dict] | None = None) -> dict` — wrapper fino sobre el SDK `openai`, devuelve el mensaje de respuesta del modelo (incluyendo `tool_calls` si el modelo decidió invocar una tool). Usado por Task 10.

**Bloqueante:** este task necesita un `NVIDIA_API_KEY` real (tier gratuito de build.nvidia.com) en `.env`. Sin esa clave, Step 4 no puede pasar — es un bloqueo externo, no de código.

- [ ] **Step 1: Escribir el test de integración (llama al endpoint real — es intencional, valida que la clave y el modelo elegido funcionan)**

`tests/test_nvidia_client.py`:

```python
from app.llm.nvidia_client import chat


def test_chat_returns_text_response():
    result = chat(messages=[{"role": "user", "content": "Responde solo con la palabra: listo"}])
    assert "content" in result
    assert isinstance(result["content"], str)
    assert len(result["content"]) > 0
```

- [ ] **Step 2: Correr el test para verificar que falla**

Run: `pytest tests/test_nvidia_client.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'app.llm.nvidia_client'`.

- [ ] **Step 3: Implementar `app/llm/__init__.py` (vacío) y `app/llm/nvidia_client.py`**

```python
```

`app/llm/nvidia_client.py`:

```python
from openai import OpenAI

from app.config.settings import settings

_client = OpenAI(base_url=settings.nvidia_base_url, api_key=settings.nvidia_api_key)

# El ID exacto se confirma contra el catálogo vigente en build.nvidia.com al momento
# de ejecutar este task — usar un modelo Instruct de la familia Llama 3.x disponible
# en el tier gratuito (p.ej. "meta/llama-3.1-70b-instruct" o el que esté vigente).
MODEL = "meta/llama-3.1-70b-instruct"


def chat(messages: list[dict], tools: list[dict] | None = None) -> dict:
    kwargs: dict = dict(model=MODEL, messages=messages, temperature=0.2, max_tokens=600)
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    response = _client.chat.completions.create(**kwargs)
    message = response.choices[0].message
    return {
        "content": message.content,
        "tool_calls": [
            {"id": tc.id, "name": tc.function.name, "arguments": tc.function.arguments}
            for tc in (message.tool_calls or [])
        ],
    }
```

- [ ] **Step 4: Poner la clave real en `.env` y correr el test**

Run:
```bash
# editar backend/.env y pegar NVIDIA_API_KEY=<clave real de build.nvidia.com>
pytest tests/test_nvidia_client.py -v
```
Expected: PASS. Si el modelo `meta/llama-3.1-70b-instruct` no existe en el catálogo vigente, el error de la API lista los IDs válidos — actualizar `MODEL` con el que corresponda y re-correr.

- [ ] **Step 5: Commit**

```bash
git add sol-de-oro-concierge/backend/app/llm sol-de-oro-concierge/backend/tests/test_nvidia_client.py
git commit -m "feat: add NVIDIA Build chat client wrapper"
```

---

### Task 9: Memoria de sesión en proceso (`app/session.py`)

**Files:**
- Create: `sol-de-oro-concierge/backend/app/session.py`
- Test: `sol-de-oro-concierge/backend/tests/test_session.py`

**Interfaces:**
- Produces:
  - `get_session(session_id: str) -> dict` — devuelve `{"history": list[dict], "party": str | None, "time_available_minutes": int | None}`, creando la sesión si no existe.
  - `append_message(session_id: str, role: str, content: str) -> None`
  - `update_context(session_id: str, **fields) -> None` — para guardar cosas como `party="couple"` o `time_available_minutes=60` (spec, Sección 18).

  Usado por Task 10.

- [ ] **Step 1: Escribir el test**

`tests/test_session.py`:

```python
from app.session import get_session, append_message, update_context


def test_new_session_starts_empty():
    session = get_session("test-session-1")
    assert session["history"] == []
    assert session["party"] is None
    assert session["time_available_minutes"] is None


def test_append_message_persists_in_session():
    append_message("test-session-2", "user", "Hola")
    append_message("test-session-2", "assistant", "¡Bienvenido!")
    session = get_session("test-session-2")
    assert session["history"] == [
        {"role": "user", "content": "Hola"},
        {"role": "assistant", "content": "¡Bienvenido!"},
    ]


def test_update_context_stores_party_and_time():
    update_context("test-session-3", party="couple", time_available_minutes=60)
    session = get_session("test-session-3")
    assert session["party"] == "couple"
    assert session["time_available_minutes"] == 60
```

- [ ] **Step 2: Correr el test para verificar que falla**

Run: `pytest tests/test_session.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'app.session'`.

- [ ] **Step 3: Implementar `app/session.py`**

```python
_SESSIONS: dict[str, dict] = {}


def get_session(session_id: str) -> dict:
    if session_id not in _SESSIONS:
        _SESSIONS[session_id] = {"history": [], "party": None, "time_available_minutes": None}
    return _SESSIONS[session_id]


def append_message(session_id: str, role: str, content: str) -> None:
    session = get_session(session_id)
    session["history"].append({"role": role, "content": content})


def update_context(session_id: str, **fields) -> None:
    session = get_session(session_id)
    session.update(fields)
```

- [ ] **Step 4: Correr el test de nuevo**

Run: `pytest tests/test_session.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add sol-de-oro-concierge/backend/app/session.py sol-de-oro-concierge/backend/tests/test_session.py
git commit -m "feat: add in-memory session context store"
```

---

### Task 10: Endpoint `POST /api/concierge`

**Files:**
- Create: `sol-de-oro-concierge/backend/app/api/__init__.py`
- Create: `sol-de-oro-concierge/backend/app/api/concierge.py`
- Modify: `sol-de-oro-concierge/backend/app/main.py` (registrar el router)
- Test: `sol-de-oro-concierge/backend/tests/test_api_concierge.py`

**Interfaces:**
- Consumes: `app.tools.supabase.*` (Task 7), `app.llm.nvidia_client.chat` (Task 8), `app.session.*` (Task 9).
- Produces: `POST /api/concierge` — request `{"message": str, "session_id": str}`, response `{"message": str, "intent": str, "actions": list[dict]}` (spec, Sección 22, formato de `actions` de la Sección 16 del blueprint original).

- [ ] **Step 1: Escribir el test end-to-end (llama al endpoint real vía `TestClient`, que a su vez llama a NVIDIA y Supabase reales — es el mismo criterio de éxito que la Task 11, pero como smoke test de que el endpoint responde con la forma correcta)**

`tests/test_api_concierge.py`:

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_concierge_endpoint_returns_expected_shape():
    response = client.post("/api/concierge", json={"message": "¿Qué habitaciones tienen?", "session_id": "test-e2e-1"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "intent" in data
    assert "actions" in data
    assert isinstance(data["actions"], list)
    assert len(data["message"]) > 0


def test_concierge_endpoint_mentions_real_room_data():
    response = client.post("/api/concierge", json={"message": "¿Cuántos metros cuadrados tiene la Grand Deluxe Suite?", "session_id": "test-e2e-2"})
    data = response.json()
    assert "80" in data["message"]
```

- [ ] **Step 2: Correr el test para verificar que falla**

Run: `pytest tests/test_api_concierge.py -v`
Expected: FAIL — `/api/concierge` no existe todavía (404).

- [ ] **Step 3: Implementar `app/api/__init__.py` (vacío) y `app/api/concierge.py`**

```python
```

`app/api/concierge.py`:

```python
import json

from fastapi import APIRouter
from pydantic import BaseModel

from app.llm.nvidia_client import chat
from app.session import append_message, get_session
from app.tools import supabase as tools

router = APIRouter()

_TOOLS_SPEC = [
    {"type": "function", "function": {"name": "get_rooms", "description": "Lista las 9 categorías de habitaciones del hotel con sus specs completas (tamaño, cama, vista, capacidad, amenidades).", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_salons", "description": "Lista los salones de eventos del hotel, opcionalmente filtrados por capacidad mínima de personas.", "parameters": {"type": "object", "properties": {"min_pax": {"type": "integer", "description": "Capacidad mínima requerida en personas"}}}}},
    {"type": "function", "function": {"name": "get_faq", "description": "Busca preguntas frecuentes sobre políticas del hotel (check-in, mascotas, tarjetas, cancelación, voltaje, moneda, idiomas, etc.), opcionalmente filtradas por tema.", "parameters": {"type": "object", "properties": {"topic": {"type": "string", "description": "Palabra clave del tema, ej: 'mascota', 'check-in', 'voltaje'"}}}}},
    {"type": "function", "function": {"name": "get_nearby", "description": "Lista lugares y actividades cerca del hotel (En el hotel, Compras, Costa, Paseos, Empresarial), opcionalmente filtrados por categoría.", "parameters": {"type": "object", "properties": {"cat": {"type": "string", "enum": ["hotel", "shopping", "coast", "paseos", "business"]}}}}},
    {"type": "function", "function": {"name": "get_restaurants", "description": "Lista los restaurantes recomendados cerca del hotel.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_cultural", "description": "Lista los lugares culturales recomendados cerca del hotel (museos, sitios históricos).", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_offers", "description": "Lista las ofertas y promociones vigentes del hotel.", "parameters": {"type": "object", "properties": {}}}},
]

_TOOL_FUNCS = {
    "get_rooms": lambda **kw: tools.get_rooms(),
    "get_salons": lambda **kw: tools.get_salons(min_pax=kw.get("min_pax")),
    "get_faq": lambda **kw: tools.get_faq(topic=kw.get("topic")),
    "get_nearby": lambda **kw: tools.get_nearby(cat=kw.get("cat")),
    "get_restaurants": lambda **kw: tools.get_restaurants(),
    "get_cultural": lambda **kw: tools.get_cultural(),
    "get_offers": lambda **kw: tools.get_offers(),
}

_SYSTEM_PROMPT = (
    "Eres el Concierge digital del hotel Sol de Oro (Miraflores, Lima). Respondes corto, claro, "
    "elegante y orientado a acción, como un concierge de hotel 5 estrellas — nunca como un chatbot "
    "genérico. Usa SIEMPRE las herramientas disponibles para obtener datos reales antes de responder "
    "sobre habitaciones, salones, políticas, lugares cercanos, restaurantes, cultura u ofertas. "
    "Nunca inventes precios, disponibilidad, horarios, capacidades o distancias. Si no tienes el dato, "
    "dilo y sugiere contactar al hotel directamente."
)


class ConciergeRequest(BaseModel):
    message: str
    session_id: str


class ConciergeResponse(BaseModel):
    message: str
    intent: str
    actions: list[dict]


_FALLBACK_MESSAGE = "Dame un momento, tengo un problema técnico para responder eso. Te recomiendo contactar directamente al hotel."
_CONTACT_ACTION = {"type": "CONTACT_HOTEL", "label": "Contactar hotel", "url": "mailto:reservas@soldeoro.pe"}


@router.post("/api/concierge", response_model=ConciergeResponse)
def concierge(payload: ConciergeRequest) -> ConciergeResponse:
    append_message(payload.session_id, "user", payload.message)
    session = get_session(payload.session_id)

    messages = [{"role": "system", "content": _SYSTEM_PROMPT}, *session["history"]]

    try:
        result = chat(messages=messages, tools=_TOOLS_SPEC)

        if result["tool_calls"]:
            messages.append({"role": "assistant", "content": result["content"] or "", "tool_calls": [
                {"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": tc["arguments"]}}
                for tc in result["tool_calls"]
            ]})
            for tc in result["tool_calls"]:
                args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                # Errores de Supabase (timeout, 5xx) se propagan y caen en el except de abajo —
                # nunca se inventa el dato faltante, se cae al mensaje de fallback (spec, "Manejo de errores").
                tool_result = _TOOL_FUNCS[tc["name"]](**args)
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": json.dumps(tool_result, ensure_ascii=False)})
            result = chat(messages=messages)

        final_message = result["content"] or _FALLBACK_MESSAGE
        actions = [] if result["content"] else [_CONTACT_ACTION]
    except Exception:
        # Captura fallos de NVIDIA Build (rate limit, timeout, modelo caído) y de Supabase
        # (tool call fallido). Nunca se propaga un 500 crudo al widget ni se inventa contenido.
        final_message = _FALLBACK_MESSAGE
        actions = [_CONTACT_ACTION]

    append_message(payload.session_id, "assistant", final_message)
    return ConciergeResponse(message=final_message, intent="UNCLASSIFIED", actions=actions)
```

**Nota de alcance:** esta primera versión no clasifica `intent` explícitamente (queda `"UNCLASSIFIED"` fijo) — el blueprint original pide un router de intención dedicado, pero para Fase 1 alcanza con que la respuesta sea correcta; la clasificación estructurada de intent/actions se refina como parte de la Fase 2 (Orchestrator), una vez que el flujo básico de datos ya está probado contra las 20 preguntas.

- [ ] **Step 4: Registrar el router en `app/main.py`**

Modificar `app/main.py`:

```python
from fastapi import FastAPI

from app.api.concierge import router as concierge_router

app = FastAPI(title="Sol de Oro Concierge")
app.include_router(concierge_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

- [ ] **Step 5: Correr el test**

Run: `pytest tests/test_api_concierge.py -v`
Expected: PASS (requiere `NVIDIA_API_KEY` válida en `.env` y las Tasks 2-7 ya migradas).

- [ ] **Step 6: Commit**

```bash
git add sol-de-oro-concierge/backend/app/api sol-de-oro-concierge/backend/app/main.py sol-de-oro-concierge/backend/tests/test_api_concierge.py
git commit -m "feat: add POST /api/concierge endpoint with tool-calling against Supabase"
```

---

### Task 11: Suite de las 20 preguntas de prueba (Sección 33 del blueprint)

**Files:**
- Create: `sol-de-oro-concierge/backend/tests/test_20_questions.py`

**Interfaces:**
- Consumes: `POST /api/concierge` (Task 10).
- Produces: reporte de cuántas de las 20 preguntas responden correctamente — es el criterio de éxito de toda la Fase 1.

- [ ] **Step 1: Escribir las 20 preguntas con su verificación de contenido (no exact-match, verificación de que el dato correcto aparece en la respuesta)**

`tests/test_20_questions.py`:

```python
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def ask(question: str, session_id: str) -> str:
    response = client.post("/api/concierge", json={"message": question, "session_id": session_id})
    assert response.status_code == 200
    return response.json()["message"]


QUESTIONS = [
    # HOTEL
    ("¿Dónde está el hotel?", ["San Martín", "Miraflores"]),
    ("¿Qué habitaciones tienen?", ["Standard", "Suite"]),
    ("¿Qué servicios ofrecen?", ["Wi-Fi", "piscina", "gimnasio", "spa"]),
    ("¿Qué instalaciones tienen?", ["piscina", "gimnasio", "spa"]),
    # EXPERIENCIAS
    ("¿Qué puedo hacer cerca del hotel?", ["Larcomar", "Malecón", "Kennedy"]),
    ("¿Qué puedo hacer caminando desde el hotel?", ["min"]),
    ("Tengo dos horas libres y quiero hacer algo caminando, ¿qué me recomiendas?", ["min"]),
    ("¿Qué puedo hacer con mi pareja cerca del hotel?", ["Parque del Amor", "Malecón", "atardecer"]),
    ("¿Qué puedo hacer en Miraflores?", ["Miraflores"]),
    # CULTURA
    ("¿Qué museos hay cerca?", ["museo", "Museo"]),
    ("¿Qué es Huaca Pucllana?", ["Huaca Pucllana", "preincaic", "pirámide", "Pirámide"]),
    ("¿Cómo voy al Centro Histórico?", ["Centro Histórico", "taxi", "min"]),
    # COMPRAS
    ("¿Dónde puedo comprar souvenirs?", ["Mercado Indio", "artesanía"]),
    ("¿Dónde está Larcomar?", ["Larcomar", "min"]),
    # EVENTOS
    ("¿Qué salones tienen?", ["Ejecutivo", "Empresarial", "Sol de Oro"]),
    ("Necesito un salón para 80 personas", ["Ejecutivo II", "Ejecutivo III", "Empresarial"]),
    ("Quiero cotizar un evento", ["comercial@soldeoro.pe", "988 861 380", "WhatsApp"]),
    # RESERVAS
    ("Quiero reservar una habitación", ["ihotelier", "reservar", "Reservar"]),
    ("Quiero contactar al hotel", ["reservas@soldeoro.pe", "610-7000", "WhatsApp"]),
    ("¿Aceptan mascotas?", ["mascota", "perro", "6 kg"]),
]


@pytest.mark.parametrize("question,expected_keywords", QUESTIONS)
def test_question_answered_with_real_data(question, expected_keywords):
    answer = ask(question, session_id=f"20q-{hash(question)}")
    assert any(kw.lower() in answer.lower() for kw in expected_keywords), (
        f"Pregunta: {question!r}\nRespuesta: {answer!r}\nEsperaba alguna de: {expected_keywords}"
    )
```

- [ ] **Step 2: Correr la suite completa**

Run: `pytest tests/test_20_questions.py -v`
Expected: idealmente 20/20 PASS. Si alguna falla, el mensaje de assert muestra la pregunta, la respuesta real y qué se esperaba — usar eso para ajustar `_SYSTEM_PROMPT` o las descripciones de las tools en Task 10 (no para inventar keywords más permisivos que oculten una respuesta realmente mala).

- [ ] **Step 3: Commit**

```bash
git add sol-de-oro-concierge/backend/tests/test_20_questions.py
git commit -m "test: add the 20 blueprint test questions as the Phase 1 success criteria"
```

---

### Task 12: Widget de chat mínimo (frontend standalone de prueba)

**Files:**
- Create: `sol-de-oro-concierge/frontend/widget/concierge.html`
- Create: `sol-de-oro-concierge/frontend/widget/concierge.css`
- Create: `sol-de-oro-concierge/frontend/widget/concierge.js`

**Interfaces:**
- Consumes: `POST http://localhost:8001/api/concierge` (Task 10, corriendo local vía `uvicorn app.main:app --port 8001`).
- Standalone — no se integra al sitio en producción en esta fase (spec, sección fuera de alcance).

- [ ] **Step 1: Crear `concierge.html` (página de prueba, no el widget embebido final)**

```html
<!doctype html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<title>Concierge · Prueba local</title>
<link rel="stylesheet" href="concierge.css"/>
</head>
<body>
<div id="concierge-root"></div>
<script src="concierge.js"></script>
</body>
</html>
```

- [ ] **Step 2: Crear `concierge.css` — paleta heredada del sitio (spec, "Elementos reutilizables")**

```css
:root{
  --gold:#b38b3a; --gold-light:#d4a85c;
  --cream:#F8F6F2; --ink:#262626; --line:#E6E2DA; --white:#FFFFFF;
}
*{box-sizing:border-box;}
body{margin:0; font-family:'Roboto',system-ui,sans-serif; background:var(--cream);}

.cc-bubble{
  position:fixed; bottom:24px; right:24px; width:56px; height:56px; border-radius:50%;
  background:var(--gold); color:#fff; border:none; cursor:pointer; font-size:1.4rem;
  box-shadow:0 8px 24px rgba(0,0,0,.22); z-index:1000;
}
.cc-bubble:hover{background:var(--gold-light);}

.cc-panel{
  position:fixed; bottom:92px; right:24px; width:360px; max-width:92vw; height:520px; max-height:78vh;
  background:var(--white); border:1px solid var(--line); border-radius:14px; box-shadow:0 20px 60px rgba(0,0,0,.22);
  display:none; flex-direction:column; overflow:hidden; z-index:1000;
}
.cc-panel.open{display:flex;}
.cc-header{padding:16px 18px; border-bottom:1px solid var(--line); font-weight:500; color:var(--ink);}
.cc-messages{flex:1; overflow-y:auto; padding:14px 16px; display:flex; flex-direction:column; gap:10px;}
.cc-msg{max-width:82%; padding:9px 13px; border-radius:12px; font-size:.86rem; line-height:1.45;}
.cc-msg.user{align-self:flex-end; background:var(--gold); color:#fff;}
.cc-msg.assistant{align-self:flex-start; background:var(--cream); color:var(--ink);}
.cc-input-row{display:flex; gap:8px; padding:12px; border-top:1px solid var(--line);}
.cc-input-row input{flex:1; padding:9px 12px; border:1px solid var(--line); border-radius:8px; font-family:inherit;}
.cc-input-row button{padding:9px 16px; background:var(--gold); color:#fff; border:none; border-radius:8px; cursor:pointer;}
```

- [ ] **Step 3: Crear `concierge.js`**

```javascript
const API_URL = "http://localhost:8001/api/concierge";
const sessionId = "widget-" + Math.random().toString(36).slice(2);

const root = document.getElementById("concierge-root");
root.innerHTML = `
  <button class="cc-bubble" id="ccToggle">💬</button>
  <div class="cc-panel" id="ccPanel">
    <div class="cc-header">Concierge · Sol de Oro</div>
    <div class="cc-messages" id="ccMessages"></div>
    <div class="cc-input-row">
      <input type="text" id="ccInput" placeholder="Escribe tu pregunta..."/>
      <button id="ccSend">Enviar</button>
    </div>
  </div>
`;

const panel = document.getElementById("ccPanel");
const messagesEl = document.getElementById("ccMessages");
const input = document.getElementById("ccInput");

document.getElementById("ccToggle").addEventListener("click", () => {
  panel.classList.toggle("open");
});

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `cc-msg ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function send() {
  const message = input.value.trim();
  if (!message) return;
  addMessage("user", message);
  input.value = "";
  try {
    const resp = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    const data = await resp.json();
    addMessage("assistant", data.message);
  } catch (err) {
    addMessage("assistant", "No pude conectarme al Concierge. Intenta de nuevo.");
  }
}

document.getElementById("ccSend").addEventListener("click", send);
input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
```

- [ ] **Step 4: Probar manualmente**

Run (dos procesos):
```bash
# proceso 1
cd sol-de-oro-concierge/backend && uvicorn app.main:app --port 8001

# proceso 2
cd sol-de-oro-concierge/frontend/widget && python -m http.server 8080
```
Abrir `http://localhost:8080/concierge.html`, click en la burbuja, escribir "¿Qué habitaciones tienen?" y confirmar que responde con datos reales (Standard Room, Suite, etc.), no un error de CORS.

**Nota:** si aparece un error de CORS en la consola del navegador, agregar `CORSMiddleware` a `app/main.py` permitiendo `http://localhost:8080` como origen — esto es exclusivo del entorno de prueba local; la configuración de CORS/CSP para producción es explícitamente de Fase 3-4 (spec, "Explícitamente fuera de alcance").

- [ ] **Step 5: Commit**

```bash
git add sol-de-oro-concierge/frontend
git commit -m "feat: add minimal standalone chat widget for local testing"
```

---

## Notas post-implementación (lo que cambió respecto al plan original)

- **Modelo real usado: `meta/llama-3.1-8b-instruct`**, no `meta/llama-3.1-70b-instruct`. El 70B tardó >2.5 min y nunca respondió (posible cold-start/capacidad del tier gratuito); un modelo de razonamiento (`nvidia/llama-3.3-nemotron-super-49b-v1.5`) tampoco sirvió porque gasta el presupuesto de tokens "pensando" y nunca llega a `content`. El 8B Instruct responde en <1s, soporta tool-calling limpio y no tiene el problema de razonamiento.
- **Guardrail anti-alucinación de contacto** (`_scrub_fabricated_contact` en `concierge.py`): en pruebas manuales el modelo inventó dos veces datos de contacto distintos (dominio falso, teléfonos falsos) pese a tenerlos correctos en el system prompt. Prompt engineering solo no bastó — se agregó un filtro determinístico por regex que elimina cualquier email/teléfono/URL que no esté en una lista blanca real antes de devolver la respuesta, y agrega el dato real si detectó algo fabricado. Cubierto por `tests/test_contact_scrubbing.py`.
- **Tool `get_contact_info` agregada** (no estaba en el diseño original): el modelo prefería invocar una tool para datos de contacto en vez de usar solo lo que tenía en el system prompt: sin ella, alucinaba un nombre de tool inexistente (`get_contact`) y tumbaba el request.
- **Manejo defensivo de tool-calls**: nombre de tool desconocido y JSON de argumentos mal formado ahora se degradan a un resultado de error legible en vez de lanzar una excepción — esto reveló que el rate limit del tier gratuito (429) también puede aparecer de forma intermítente bajo uso intenso; el `except Exception` genérico ya lo cubre correctamente cayendo al mensaje de fallback.
- **Prompt de brevedad**: el modelo por defecto listaba las 9 habitaciones en detalle exhaustivo y la respuesta se cortaba a mitad de frase por `max_tokens`. Se ajustó el prompt para mencionar 2-3 opciones concretas (nunca cero) y preguntar qué le interesa al huésped, en vez de listarlo todo.
- **Suite de 20 preguntas con pausa de 2s entre llamadas**: sin esto, las ~23 llamadas seguidas de la suite completa topaban el rate limit del tier gratuito de forma reproducible cerca del final.
- **Test de regresión nuevo** (`test_no_fabricated_contact_info` en `test_20_questions.py`): ninguna de las 20 preguntas originales detectaba contacto inventado porque solo verifican que el dato correcto esté presente, no que no haya datos de más. Se agregó específicamente tras encontrar el bug en la prueba manual del widget (Task 12).

## Verificación final de la Fase 1

- [ ] Las 3 tablas nuevas (`rooms`, `salons`, `hotel_faq`) existen en Supabase con RLS, con 9 + 9 + 22 filas respectivamente.
- [ ] `le_experiences` tiene exactamente 19 filas activas, agrupadas en `hotel`/`shopping`/`coast`/`paseos`/`business`.
- [ ] `admin/index.html` refleja las categorías nuevas de `le_experiences` en su formulario.
- [ ] `pytest` corre verde en `sol-de-oro-concierge/backend/tests/` completo, incluyendo `test_20_questions.py`.
- [ ] El widget standalone responde preguntas reales contra `localhost:8001` sin errores de CORS.
- [ ] Nada del sitio en `soldeoro.com.pe` (HTML/CSS/JS de producción) fue tocado salvo `admin/index.html` (Task 6, Step 3) — el widget y el backend viven enteramente en `sol-de-oro-concierge/`, separados del sitio.
