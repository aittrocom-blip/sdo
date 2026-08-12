import os
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
        f"{SUPA_URL}/rest/v1/salons",
        headers={
            "apikey": SUPA_KEY,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json=SALONS,
        timeout=30,
    )
    print(resp.status_code, len(resp.json()) if resp.status_code == 201 else resp.text[:500])
    resp.raise_for_status()


if __name__ == "__main__":
    main()
