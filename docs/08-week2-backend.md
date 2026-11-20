# Week 2 — Backend Foundation

## Delivered starter
- FastAPI app with OpenAPI docs.
- Health endpoint.
- Machine registration and listing.
- Measurement ingestion and history.
- SQLAlchemy models.
- SQLite local development; PostgreSQL via environment variable.
- Docker Compose for PostgreSQL + API.
- API demo script.

## API examples
### Register a machine
```http
POST /api/machines
Content-Type: application/json

{"code":"M-001","name":"Demo Motor","asset_type":"rotating_machine"}
```

### Submit a measurement
```http
POST /api/measurements
Content-Type: application/json

{
  "machine_code":"M-001",
  "timestamp":"2026-11-20T20:00:00Z",
  "product_type":"M",
  "air_temperature_k":300.0,
  "process_temperature_k":310.0,
  "rotational_speed_rpm":1500,
  "torque_nm":40,
  "tool_wear_min":100
}
```

## Remaining Week 2 items
- Wire the frozen ML predictor into the ingestion pipeline.
- Add Prediction and Alert persistence models.
- Add Alembic migrations instead of `create_all`.
- Add API tests with an isolated test database.
- Add CSV batch ingestion and robust duplicate handling.
