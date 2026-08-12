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
