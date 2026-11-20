from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def unique_code():
    return "T-" + uuid.uuid4().hex[:8]

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in {"ok", "degraded"}

def test_machine_and_measurement_flow():
    code = unique_code()
    created = client.post("/api/machines", json={"code": code, "name": "Test motor", "asset_type": "rotating_machine"})
    assert created.status_code == 201
    assert created.json()["code"] == code

    measurement = client.post("/api/measurements", json={
        "machine_code": code,
        "product_type": "M",
        "air_temperature_k": 300,
        "process_temperature_k": 310,
        "rotational_speed_rpm": 1500,
        "torque_nm": 40,
        "tool_wear_min": 100
    })
    assert measurement.status_code == 201
    body = measurement.json()
    assert body["measurement"]["machine_code"] == code
    assert body["inference_status"] == "not_integrated"

    history = client.get(f"/api/machines/{code}/measurements")
    assert history.status_code == 200
    assert len(history.json()) == 1

def test_duplicate_machine_code_returns_conflict():
    code = unique_code()
    payload = {"code": code, "name": "Test motor", "asset_type": "rotating_machine"}
    assert client.post("/api/machines", json=payload).status_code == 201
    assert client.post("/api/machines", json=payload).status_code == 409

def test_invalid_measurement_is_rejected():
    response = client.post("/api/measurements", json={
        "machine_code": "missing",
        "product_type": "M",
        "air_temperature_k": 999,
        "process_temperature_k": 310,
        "rotational_speed_rpm": 1500,
        "torque_nm": 40,
        "tool_wear_min": 100
    })
    assert response.status_code == 422
