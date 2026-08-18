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


# site_section: cada fila debe traer la sección REAL del sitio donde el huésped puede
# ampliar la información — es el dato que el Concierge usa para guiar sin inventar.
def test_get_rooms_site_section():
    rooms = get_rooms()
    assert all(r["site_section"] == "Habitaciones" for r in rooms)


def test_get_salons_site_section():
    salons = get_salons()
    assert all("Eventos" in s["site_section"] for s in salons)


def test_get_nearby_site_section_matches_category():
    coast = get_nearby(cat="coast")
    assert all(item["site_section"] == "Experiencias → Costa" for item in coast)
    hotel = get_nearby(cat="hotel")
    assert all(item["site_section"] == "Experiencias → En el Hotel" for item in hotel)


def test_get_restaurants_site_section():
    restaurants = get_restaurants()
    assert all(r["site_section"] == "Experiencias → Gastronomía" for r in restaurants)


def test_get_cultural_site_section():
    cultural = get_cultural()
    assert all(c["site_section"] == "Experiencias → Cultura" for c in cultural)
