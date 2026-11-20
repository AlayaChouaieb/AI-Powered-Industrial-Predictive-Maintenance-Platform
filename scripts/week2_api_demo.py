"""Small API smoke-test/demo script. Start the API first: uvicorn app.main:app --reload."""
import json
import urllib.request
from datetime import datetime, timezone

BASE = "http://127.0.0.1:8000"

def request(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

try:
    machine = request("/api/machines", "POST", {"code": "M-001", "name": "Demo Motor", "asset_type": "rotating_machine"})
except Exception as exc:
    if getattr(exc, "code", None) == 409:
        machine = {"code": "M-001"}
    else:
        raise

measurement = request("/api/measurements", "POST", {
    "machine_code": "M-001",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "product_type": "M",
    "air_temperature_k": 300.0,
    "process_temperature_k": 310.0,
    "rotational_speed_rpm": 1500,
    "torque_nm": 40,
    "tool_wear_min": 100,
})
print(json.dumps(measurement, indent=2))
