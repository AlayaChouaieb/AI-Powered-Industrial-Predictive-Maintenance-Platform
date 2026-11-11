"""Week 1 demo: score hand-built scenarios and replay validation rows through the frozen models.
Run from repo root:  python scripts/week1_demo.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ml" / "src"))
import warnings; warnings.filterwarnings("ignore")
import pandas as pd
from pm_ml import config as C
from pm_ml.predict import Predictor, ValidationError
from pm_ml.split import load_split

pred = Predictor()
base = {"product_type": "M", "air_temperature_k": 300.0, "process_temperature_k": 310.1,
        "rotational_speed_rpm": 1500, "torque_nm": 40.0, "tool_wear_min": 100}
scenarios = {
    "1 typical normal operation": base,
    "2 low speed + small temp difference (HDF rule region)": dict(base, process_temperature_k=308.2, rotational_speed_rpm=1300),
    "3 high power (PWF rule region)": dict(base, torque_nm=65.0, rotational_speed_rpm=1700),
    "4 high wear x torque, L product (OSF rule region)": dict(base, product_type="L", torque_nm=60.0, tool_wear_min=200),
    "5 very high tool wear only": dict(base, tool_wear_min=235),
}
rows = []
print("=== Hand-built scenarios (NOT dataset rows) ===")
for name, p in scenarios.items():
    r = pred.predict(p)
    rows.append({"scenario": name, "status": r["status"], "failure_risk": round(r["failure_risk"], 3),
                 "predicted_class": r["fault"]["predicted_class"], "anomaly_score": round(r["anomaly"]["score"], 3),
                 "is_anomaly": r["anomaly"]["is_anomaly"]})
print(pd.DataFrame(rows).to_string(index=False))

print("\n=== Example API-style response for scenario 2 ===")
print(json.dumps(pred.predict(scenarios["2 low speed + small temp difference (HDF rule region)"]), indent=2))

print("\n=== Validation rejects malformed payload ===")
try:
    pred.predict(dict(base, torque_nm=-3))
except ValidationError as e:
    print("rejected:", e)

print("\n=== Replay of validation rows with SIMULATED machine ids (AI4I has none) ===")
_, val, _ = load_split()
sample = pd.concat([val[val.fault_class == "none"].head(4), val[val.fault_class != "none"].head(6)]).reset_index(drop=True)
res = pred.predict_batch(sample[C.INPUT_COLUMNS].to_dict("records"))
out = pd.DataFrame({"machine_id": [f"M-{i % 4 + 1:03d}" for i in range(len(sample))],
                    "true_label": sample.fault_class,
                    "status": [r["status"] for r in res],
                    "failure_risk": [round(r["failure_risk"], 3) for r in res],
                    "pred_class": [r["fault"]["predicted_class"] for r in res],
                    "anomaly": [r["anomaly"]["is_anomaly"] for r in res]})
print(out.to_string(index=False))
Path(C.REPORT_DIR / "week1_demo_output.txt").write_text(out.to_string(index=False))
