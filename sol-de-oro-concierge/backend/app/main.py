from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.concierge import router as concierge_router

app = FastAPI(title="Sol de Oro Concierge")

# Exclusivo del entorno de prueba local (Task 12): permite que el widget standalone
# (localhost:8080) y el sitio real servido en local (localhost:8000, ver el bloque
# "AI CONCIERGE — prueba local temporal" en index.html) llamen a este backend en
# localhost:8001. La configuración de CORS/CSP para producción se decide en Fase 3-4,
# cuando el widget se integre al sitio real desplegado — no antes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8000"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

app.include_router(concierge_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
