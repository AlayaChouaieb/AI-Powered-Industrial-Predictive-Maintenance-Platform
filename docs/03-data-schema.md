# 03 - Data Schema and Prediction Outputs

Based on UCI AI4I 2020. **Updated after Week 1** (Days 2-5 decisions are final unless noted).

## Source columns -> API fields
| AI4I column | API field | Type / unit | Available at prediction time |
|---|---|---|---|
| Type (L/M/H) | `product_type` | enum | yes |
| Air temperature [K] | `air_temperature_k` | float, K | yes |
| Process temperature [K] | `process_temperature_k` | float, K | yes |
| Rotational speed [rpm] | `rotational_speed_rpm` | float, rpm | yes |
| Torque [Nm] | `torque_nm` | float, Nm | yes |
| Tool wear [min] | `tool_wear_min` | float, min | yes |
| UDI, Product ID | - | identifiers | no (not features) |
| Machine failure, TWF, HDF, PWF, OSF, RNF | - | labels | **no (targets only, never features)** |

AI4I has no timestamps or true machine IDs. The simulator/CSV replay assigns `machine_id` (e.g. 5-8 simulated machines) and `timestamp`. This is a documented assumption.

## Measurement payload (`POST /api/measurements`)
```json
{
  "machine_id": "M-001",
  "timestamp": "2026-11-12T09:30:00Z",
  "product_type": "M",
  "air_temperature_k": 298.1,
  "process_temperature_k": 308.6,
  "rotational_speed_rpm": 1551,
  "torque_nm": 42.8,
  "tool_wear_min": 108
}
```
Validation (implemented in `ml/src/pm_ml/predict.py`, ranges in `models/feature_config.json`): all six fields required, `product_type` in {L,M,H}, air 250-400 K, process 250-450 K, speed 1-10,000 rpm, torque 0-500 Nm, tool wear 0-1000 min, finite numbers only. `machine_id` and ISO-8601 `timestamp` are validated by the API layer (Day 6-7).

## Prediction output (as returned by `Predictor.predict`)
```json
{
  "anomaly": { "score": 0.521, "threshold": 0.566, "is_anomaly": false },
  "failure_risk": 0.34,
  "fault": {
    "predicted_class": "none",
    "probabilities": { "none": 0.66, "TWF": 0.0, "HDF": 0.323, "PWF": 0.0, "OSF": 0.0, "other": 0.017 },
    "most_likely_failure_mode": "HDF",
    "supported_modes": ["HDF", "PWF", "OSF"]
  },
  "status": "critical",
  "top_factors": [],
  "model_version": "0.1.0",
  "note": "Decision-support signal from a model trained on synthetic data; not a failure guarantee."
}
```
- `failure_risk` = 1 - P(none). **Show this plus `most_likely_failure_mode`**; `predicted_class` is the arg-max and can be `none` while status is `critical`.
- **Classes (final):** `none`, `TWF`, `HDF`, `PWF`, `OSF`, `other`. Only **HDF, PWF, OSF** are supported predictions; TWF and `other` probabilities are returned but must not be presented as reliable (Week 1 report, section 6).
- `top_factors` is empty until Day 13 (local explanations).
- **Anomaly score:** higher = more unusual; threshold = 95th percentile of validation normal scores.

## Health status rules (provisional, `models/thresholds.json`)
| Status | Rule |
|---|---|
| critical | `failure_risk` >= 0.2767 |
| warning | `failure_risk` >= 0.09, or anomaly score >= 0.566 |
| healthy | otherwise |

Thresholds are derived on training out-of-fold predictions (and the anomaly threshold on validation); see `docs/06-week1-report.md`, section 5. An alert is created on transition into warning/critical; a cooldown prevents new alerts for the same machine and status while one is open (Day 9).
Alert states: `open` -> `acknowledged` -> `resolved`, with an optional `note`.
