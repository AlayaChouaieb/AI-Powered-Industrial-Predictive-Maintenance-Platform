"""Seed one machine and demo measurements using the API."""
import json
import urllib.request
from datetime import datetime, timezone, timedelta

BASE = "http://localhost:8000"

def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(), method="POST", headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

try:
    post("/api/machines", {"code":"M-001","name":"Demo Motor","asset_type":"rotating_machine"})
    print("Created M-001")
except Exception as exc:
    if getattr(exc, "code", None) == 409:
        print("M-001 already exists")
    else:
        raise

for i in range(10):
    post("/api/measurements", {
        "machine_code":"M-001",
        "timestamp":(datetime.now(timezone.utc)-timedelta(minutes=10-i)).isoformat(),
        "product_type":"M",
        "air_temperature_k":300+i*0.2,
        "process_temperature_k":310+i*0.2,
        "rotational_speed_rpm":1500-i*5,
        "torque_nm":40+i*0.5,
        "tool_wear_min":100+i*2
    })
print("Seeded 10 measurements.")
