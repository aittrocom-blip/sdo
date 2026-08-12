import os
import requests

SUPA_URL = "https://fjzshpilzjtfjcouzzzz.supabase.co"
SUPA_KEY = "sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY"
BUCKET = f"{SUPA_URL}/storage/v1/object/public/experiences/rooms"

ROOMS = [
    dict(sort_order=1, category="01 · Esencial", name="Standard Room",
         description="Esta habitación cuenta con una cama matrimonial, baño privado con bañera y secador de pelo, aire acondicionado, TV de pantalla plana con cable, entrada privada, paredes insonorizadas y armario.",
         size_m2=25, size_ft2=269, bed="1 Cama matrimonial", view="Exterior", capacity_people=2,
         features=["Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con bañera", "Smart TV cable"],
         photo_url=f"{BUCKET}/FOTOS-WEB-SOL-DE-ORO_11zon-1.jpg"),
    dict(sort_order=2, category="02 · Esencial", name="Standard Room Twin",
         description="Esta habitación cuenta con dos camas twin (100×200 cm), baño privado con bañera y secador de pelo, aire acondicionado, TV de pantalla plana, entrada privada, paredes insonorizadas y armario.",
         size_m2=25, size_ft2=269, bed="2 Twin (100×200 cm)", view="Exterior", capacity_people=2,
         features=["Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con bañera", "Smart TV cable"],
         photo_url=f"{BUCKET}/FOTOS-WEB-SOL-DE-ORO-1_2_11zon.jpg"),
    dict(sort_order=3, category="03 · Confort", name="Superior King Room",
         description="La habitación cuenta con una cama king, aire acondicionado, entrada privada y baño privado con ducha y secador de pelo. Armario, caja fuerte y TV de pantalla plana con cable.",
         size_m2=27, size_ft2=291, bed="1 Cama King", view="Miraflores", capacity_people=2,
         features=["Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con ducha", "Smart TV cable"],
         photo_url=f"{BUCKET}/FOTOS-WEB-SOL-DE-ORO-2_11zon.jpg"),
    dict(sort_order=4, category="04 · Confort", name="Superior Twin Room",
         description="La habitación cuenta con dos camas queen, aire acondicionado, entrada privada y baño privado con ducha y secador de pelo. Armario, caja fuerte y TV de pantalla plana con cable.",
         size_m2=27, size_ft2=291, bed="2 Camas Queen", view="Miraflores", capacity_people=2,
         features=["Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con ducha", "Smart TV cable"],
         photo_url=f"{BUCKET}/FOTOS-WEB-SOL-DE-ORO-3_11zon.jpg"),
    dict(sort_order=5, category="05 · Suite", name="Junior Suite",
         description="La habitación cuenta con cama king, aire acondicionado, armario, caja fuerte, TV de pantalla plana con canales y baño privado con ducha y secador de pelo.",
         size_m2=40, size_ft2=431, bed="1 Cama King", view="Miraflores", capacity_people=3,
         features=["Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con ducha", "Smart TV cable"],
         photo_url=f"{BUCKET}/JUNIOR-SUITE_11zon.jpg"),
    dict(sort_order=6, category="06 · Suite", name="Junior Suite Twin",
         description="La habitación cuenta con dos camas queen, aire acondicionado, armario, caja fuerte, TV de pantalla plana con canales y baño privado con ducha y secador de pelo.",
         size_m2=40, size_ft2=431, bed="2 Camas Queen", view="Miraflores", capacity_people=3,
         features=["Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con ducha", "Smart TV cable"],
         photo_url=f"{BUCKET}/JUNIOR-SUITE-TWIN_11zon.jpg"),
    dict(sort_order=7, category="07 · Premium", name="Executive Suite",
         description="La habitación cuenta con una cama king, aire acondicionado, armario, caja fuerte y TV de pantalla plana con cable. Cuenta con sala interna, baño privado con ducha y secador de pelo.",
         size_m2=80, size_ft2=861, bed="1 Cama King", view="Miraflores · piso alto", capacity_people=2,
         features=["Sala interna", "Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con ducha", "Smart TV cable"],
         photo_url=f"{BUCKET}/FOTOS-WEB-SOL-DE-ORO_11zon.jpg"),
    dict(sort_order=8, category="08 · Premium", name="Suite Deluxe",
         description="La habitación cuenta con dos camas queen, aire acondicionado, jacuzzi interno, armario, caja fuerte, TV de pantalla plana con canales y baño privado con ducha y secador de pelo.",
         size_m2=80, size_ft2=861, bed="2 Camas Queen", view="Miraflores · piso alto", capacity_people=2,
         features=["Jacuzzi interno", "Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Baño con ducha", "Smart TV cable"],
         photo_url=f"{BUCKET}/FOTOS-WEB-SOL-DE-ORO-5_11zon.jpg"),
    dict(sort_order=9, category="09 · Insignia", name="Grand Deluxe Suite",
         description="La habitación cuenta con una cama king, área de estar, aire acondicionado, armario, caja fuerte y TV de pantalla plana con cable. Cuenta con jacuzzi interno, sala interna, baño privado con ducha y secador de pelo.",
         size_m2=80, size_ft2=861, bed="1 Cama King", view="Miraflores · piso alto", capacity_people=2,
         features=["Jacuzzi interno", "Sala de estar", "Aire acondicionado", "Caja fuerte", "Minibar", "Cortinas blackout", "Smart TV cable"],
         photo_url=f"{BUCKET}/FOTOS-WEB-SOL-DE-ORO-3_11zon-1.jpg"),
]


def login() -> str:
    r = requests.post(
        f"{SUPA_URL}/auth/v1/token?grant_type=password",
        headers={"apikey": SUPA_KEY, "Content-Type": "application/json"},
        json={"email": os.environ["ADMIN_EMAIL"], "password": os.environ["ADMIN_PASSWORD"]},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def main() -> None:
    token = login()
    resp = requests.post(
        f"{SUPA_URL}/rest/v1/rooms",
        headers={
            "apikey": SUPA_KEY,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json=ROOMS,
        timeout=30,
    )
    print(resp.status_code, len(resp.json()) if resp.status_code == 201 else resp.text[:500])
    resp.raise_for_status()


if __name__ == "__main__":
    main()
