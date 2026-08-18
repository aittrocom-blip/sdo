import httpx

from app.config.settings import settings

_HEADERS = {"apikey": settings.supabase_anon_key}

# Mapea cada dominio de datos a la sección REAL donde vive en el sitio, con el mismo
# texto que ve el huésped en pantalla (mismas etiquetas que CAT_LABELS en admin/index.html
# y las mismas pestañas de experiencias.html). Esto es lo único que el modelo puede citar
# como "dónde encontrar más información" — nunca debe inventar una sección que no esté acá.
_NEARBY_CAT_SECTION = {
    "hotel": "Experiencias → En el Hotel",
    "shopping": "Experiencias → Compras · Ocio",
    "coast": "Experiencias → Costa",
    "paseos": "Experiencias → Paseos",
    "business": "Experiencias → Empresarial",
}


def _get(path: str, params: dict) -> list[dict]:
    resp = httpx.get(f"{settings.supabase_url}/rest/v1/{path}", headers=_HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _post(path: str, body: dict) -> dict:
    headers = {**_HEADERS, "Content-Type": "application/json", "Prefer": "return=representation"}
    resp = httpx.post(f"{settings.supabase_url}/rest/v1/{path}", headers=headers, json=body, timeout=15)
    resp.raise_for_status()
    rows = resp.json()
    return rows[0] if rows else {}


def _with_section(rows: list[dict], section: str) -> list[dict]:
    for row in rows:
        row["site_section"] = section
    return rows


def get_rooms() -> list[dict]:
    rows = _get("rooms", {"select": "*", "active": "eq.true", "order": "sort_order"})
    return _with_section(rows, "Habitaciones")


def get_salons(min_pax: int | None = None) -> list[dict]:
    params = {"select": "*", "active": "eq.true", "order": "sort_order"}
    if min_pax is not None:
        params["capacity_max"] = f"gte.{min_pax}"
    rows = _get("salons", params)
    return _with_section(rows, "Eventos → tabla de capacidad por salón")


def get_faq(topic: str | None = None) -> list[dict]:
    params = {"select": "*", "active": "eq.true", "order": "sort_order"}
    if topic:
        params["or"] = f"(question.ilike.*{topic}*,answer.ilike.*{topic}*)"
    rows = _get("hotel_faq", params)
    return _with_section(rows, "Preguntas frecuentes (FAQ)")


def get_nearby(cat: str | None = None) -> list[dict]:
    params = {"select": "*", "active": "eq.true", "order": "sort_order"}
    if cat:
        params["cat"] = f"eq.{cat}"
    rows = _get("le_experiences", params)
    for row in rows:
        row["site_section"] = _NEARBY_CAT_SECTION.get(row.get("cat"), "Experiencias")
    return rows


def get_restaurants() -> list[dict]:
    rows = _get("le_restaurants", {"select": "*", "active": "eq.true", "order": "sort_order"})
    return _with_section(rows, "Experiencias → Gastronomía")


def get_cultural() -> list[dict]:
    rows = _get("le_cultural", {"select": "*", "active": "eq.true", "order": "sort_order"})
    return _with_section(rows, "Experiencias → Cultura")


def get_offers() -> list[dict]:
    rows = _get("offers", {"select": "*", "active": "eq.true", "order": "sort_order"})
    return _with_section(rows, "Ofertas")


def insert_lead(fields: dict) -> dict:
    return _post("concierge_leads", fields)
