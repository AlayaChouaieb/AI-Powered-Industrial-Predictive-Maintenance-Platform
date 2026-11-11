# 04 - Architecture Sketch

A **modular monolith**: one FastAPI service, one PostgreSQL database, one frontend. No microservices.

## Components
```mermaid
flowchart LR
  SRC[CSV replay / simulator] -->|POST /api/measurements| API
  UI[Dashboard] <-->|REST / JSON| API
  subgraph Backend [FastAPI service]
    API[API layer + Pydantic validation]
    SVC[Prediction service]
    ALR[Alert rules]
    MOD[(Model artifacts)]
    API --> SVC --> MOD
    SVC --> ALR
  end
  API --> DB[(PostgreSQL)]
  ALR --> DB
```

## Data flow
Measurement input -> API validation -> PostgreSQL -> ML inference -> prediction/alert storage -> dashboard.

## Design decisions
- Models and preprocessing are loaded **once at startup**, with the same feature order as in training.
- ML code in `ml/` produces artifacts in `models/`; the backend only loads and serves them.
- Alembic migrations for all schema changes.
- Config via environment variables; structured logging.
- Docker Compose is optional (cut-list item 4).

## Database model (initial)
```mermaid
erDiagram
  MACHINES ||--o{ MEASUREMENTS : has
  MEASUREMENTS ||--|| PREDICTIONS : produces
  MACHINES ||--o{ ALERTS : raises
  PREDICTIONS ||--o{ ALERTS : triggers
  MACHINES { int id PK string code UK string name string asset_type datetime created_at }
  MEASUREMENTS { int id PK int machine_id FK datetime ts string product_type float air_temperature_k float process_temperature_k float rotational_speed_rpm float torque_nm float tool_wear_min }
  PREDICTIONS { int id PK int measurement_id FK float anomaly_score bool is_anomaly string fault_class json fault_probs json top_factors string status string model_version datetime created_at }
  ALERTS { int id PK int machine_id FK int prediction_id FK string severity string state string note datetime created_at datetime updated_at }
```

## API surface
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/machines | Register a machine |
| GET | /api/machines | List machines + latest status |
| POST | /api/measurements | Submit measurement, trigger inference |
| GET | /api/machines/{id}/history | Measurement + prediction history |
| GET | /api/alerts | Active and historical alerts |
| PATCH | /api/alerts/{id} | Acknowledge / resolve |
| GET | /health | Health check (Day 6) |

## Frontend pages
Overview (counts, alerts, recent predictions) / Machine detail (trends, predictions, explanation) / Alerts and history (workflow).
