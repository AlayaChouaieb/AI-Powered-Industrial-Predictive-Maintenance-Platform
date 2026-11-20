# Weeks 1–4 Execution Plan

Project: AI-Powered Industrial Predictive Maintenance Platform (MotorGuard AI)

## Week 1 — Project framing and ML feasibility (completed in existing repository)
- Define the problem, scope, user stories and Definition of Done.
- Select UCI AI4I 2020 dataset and document synthetic-data limitations.
- Audit data, define feature/target separation, establish fixed train/validation/test split.
- Build preprocessing pipeline, train baselines, evaluate classifier and anomaly detector.
- Freeze model artifacts and document feasibility gate.
**Existing evidence:** `docs/01-scope.md` through `docs/06-week1-report.md`, `ml/`, `models/`, `reports/`.

## Week 2 — Backend foundation
- FastAPI service and typed request/response schemas.
- PostgreSQL persistence for machines and measurements.
- Health endpoint, machine CRUD/listing and measurement ingestion.
- Add prediction service boundary; do not fabricate predictions if model artifacts are unavailable.
- Unit/API tests and API documentation.

**Acceptance:** API starts; health returns OK; machine registration works; valid measurements persist; invalid payloads return 422; database survives restart.

## Week 3 — Dashboard and workflow
- Overview page with machine cards and latest measurements.
- Machine history view.
- Alerts view with acknowledgement/resolution states.
- API-connected dashboard; clear loading/error/empty states.
- Show synthetic-data and decision-support caveats.

**Acceptance:** dashboard consumes API data; a seeded machine and measurements appear; status is visibly labelled as demo/placeholder until inference is integrated.

## Week 4 — Integration, deployment and demo readiness
- Docker Compose for API + PostgreSQL (+ MQTT broker as optional extension).
- Environment configuration and health checks.
- Seed/demo data script.
- Automated tests and smoke-test checklist.
- README setup instructions and architecture diagrams.
- Record a reproducible end-to-end demo.

**Acceptance:** `docker compose up --build` starts services; seed script creates demo data; API and dashboard can be shown; tests pass.

## Current implementation notes
Week 1 ML work already exists in this repository. The Week 2–4 starter files added alongside this roadmap are a scaffold and must be tested locally before claiming a complete end-to-end deployment. Model integration and dashboard/API wiring should be reviewed against the current ML package interfaces.
