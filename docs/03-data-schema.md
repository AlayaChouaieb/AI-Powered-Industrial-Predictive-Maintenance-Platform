# 03 - Data Schema and Prediction Outputs

Based on UCI AI4I 2020. Items marked (Day 2) are confirmed after data inspection.

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
Validation (initial; tighten on Day 2 from observed ranges): required fields, `product_type` in {L,M,H}, temperatures 250-400 K, speed > 0, torque >= 0, tool wear >= 0, ISO-8601 timestamp.

## Prediction output
```json
{
  "measurement_id": 1234,
  "anomaly": { "score": 0.62, "threshold": 0.55, "is_anomaly": true },
  "fault": {
    "predicted_class": "HDF",
    "probabilities": { "none": 0.18, "TWF": 0.02, "HDF": 0.71, "PWF": 0.05, "OSF": 0.04 }
  },
  "top_factors": [
    { "feature": "temperature_difference", "direction": "high", "note": "correlated with this prediction, not causal proof" }
  ],
  "status": "warning",
  "model_version": "0.1.0"
}
```
- **Fault classes (proposed, Day 2/4):** `none`, `TWF`, `HDF`, `PWF`, `OSF`. RNF (random failures) is essentially unpredictable and very rare; decide on exclusion/merge on Day 2. AI4I rows can carry several failure modes; decide single-label vs multi-label on Day 2.
- **Fault classifier may be absent** if the Day 5 gate fails; the API field then becomes null.
- **Anomaly score:** higher = more unusual; threshold chosen on validation data (Day 5).

## Health status and alert rules (initial; tuned Day 5/9)
| Status | Rule |
|---|---|
| healthy | not anomalous and no high-risk class |
| warning | anomaly score >= threshold, or failure-class probability >= p_warn |
| critical | anomaly AND failure-class probability >= p_crit |

An alert is created on transition into warning/critical; a cooldown prevents new alerts for the same machine and status while one is open.
Alert states: `open` -> `acknowledged` -> `resolved`, with an optional `note`.
