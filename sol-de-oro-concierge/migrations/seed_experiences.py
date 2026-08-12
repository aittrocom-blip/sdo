import os
import requests

SUPA_URL = "https://fjzshpilzjtfjcouzzzz.supabase.co"
SUPA_KEY = "sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY"
BUCKET = f"{SUPA_URL}/storage/v1/object/public/experiences"


def login() -> str:
    r = requests.post(
        f"{SUPA_URL}/auth/v1/token?grant_type=password",
        headers={"apikey": SUPA_KEY, "Content-Type": "application/json"},
        json={"email": os.environ["ADMIN_EMAIL"], "password": os.environ["ADMIN_PASSWORD"]},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"]


EXPERIENCES = [
    # cat=hotel
    dict(sort_order=1, mode="modern", cat="hotel", title="Piscina temperada", zone="En el hotel",
         excerpt="Piscina temperada en la terraza del piso 14, climatizada todo el año con vista a Miraflores.",
         tag="En el hotel · Piso 14", photo_url=f"{BUCKET}/explore/piscina-hotel.webp",
         maps_url="https://maps.google.com/?q=Sol+de+Oro+Hotel+Suites+Miraflores"),
    dict(sort_order=2, mode="modern", cat="hotel", title="Gimnasio 24h", zone="En el hotel",
         excerpt="Equipamiento Technogym, peso libre y cardio con vista al Pacífico, abierto las 24 horas.",
         tag="En el hotel · Gimnasio", photo_url=f"{BUCKET}/explore/gimnasio-hotel.jpg",
         maps_url="https://maps.google.com/?q=Sol+de+Oro+Hotel+Suites+Miraflores"),
    dict(sort_order=3, mode="modern", cat="hotel", title="Spa & Masajes", zone="En el hotel",
         excerpt="Rituales con tradición peruana, sauna seco, hidromasaje y cabinas de pareja. Reserva con anticipación.",
         tag="En el hotel · Spa", photo_url=f"{BUCKET}/explore/spa-hotel.jpg",
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

    del_resp = requests.delete(
        f"{SUPA_URL}/rest/v1/le_experiences?id=neq.00000000-0000-0000-0000-000000000000",
        headers=headers,
        timeout=30,
    )
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
