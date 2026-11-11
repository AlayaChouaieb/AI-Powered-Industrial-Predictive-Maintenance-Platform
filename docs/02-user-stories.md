# 02 - User Stories

Persona: **Maintenance technician / reliability engineer** reviewing machine health.

## US-1 Inspect a machine (Must)
As a maintenance user, I want to see a list of machines with their latest health status, so I can decide which to look at first.
- Overview lists machines with status (healthy / warning / critical), last update time, open alert count.
- A machine can be registered via API; unknown machine IDs are rejected on ingestion.

## US-2 Submit measurements (Must)
As a user (or data source), I want to submit measurements via API or CSV, so the system can assess machine behavior.
- `POST /api/measurements` accepts the schema in `03-data-schema.md`.
- Malformed or out-of-range payloads return a consistent 422 error and are not stored.
- A valid submission is stored and returns the prediction result.

## US-3 View anomaly status (Must)
As a user, I want to see whether a machine is behaving unusually, with a score, so I can judge urgency.
- Each measurement shows anomaly score, threshold, and is_anomaly flag.
- Machine detail shows a trend of measurements and anomaly scores over time.
- UI states the score is not a guaranteed failure probability.

## US-4 Review fault prediction (Must; explanation Should)
As a user, I want the predicted fault category with probabilities and main contributing factors, so I can prepare the right intervention.
- Shows predicted class and per-class probabilities, with timestamp and input values.
- Shows top contributing features in plain language (feature importance/SHAP if time permits), noting it is not causal proof.

## US-5 Acknowledge an alert (Must)
As a user, I want to acknowledge or resolve an alert and leave a note, so the team knows it is being handled.
- Alert lifecycle: open -> acknowledged -> resolved (`PATCH /api/alerts/{id}`).
- Optional maintenance note is stored with the alert.
- Repeated similar alerts on the same machine are suppressed by a cooldown / state-transition rule.
