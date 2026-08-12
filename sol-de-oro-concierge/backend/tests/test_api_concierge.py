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
