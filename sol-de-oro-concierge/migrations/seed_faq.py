import os
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
        f"{SUPA_URL}/rest/v1/hotel_faq",
        headers={
            "apikey": SUPA_KEY,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json=FAQ,
        timeout=30,
    )
    print(resp.status_code, len(resp.json()) if resp.status_code == 201 else resp.text[:500])
    resp.raise_for_status()


if __name__ == "__main__":
    main()
