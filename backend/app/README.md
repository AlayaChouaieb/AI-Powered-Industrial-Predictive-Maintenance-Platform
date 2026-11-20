# Backend API (Week 2 starter)

## Local run
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

By default, development uses SQLite at `backend/motorguard.db`. Set `DATABASE_URL` for PostgreSQL.

Endpoints:
- `GET /health`
- `POST /api/machines`
- `GET /api/machines`
- `POST /api/measurements`
- `GET /api/machines/{machine_code}/measurements`

Interactive API docs: `/docs`.

**Important:** this starter persists measurements but does not yet call the frozen ML predictor. It explicitly reports `inference_status=not_integrated`; do not treat stored telemetry as a prediction.
