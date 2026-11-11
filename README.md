# AI-Powered Industrial Predictive Maintenance Platform

A 3-week prototype web platform that ingests machine measurements, runs **anomaly detection** and **fault classification**, stores results, and shows alerts to a maintenance user.

> **Status:** Day 1 complete (scope, user stories, schema, architecture, repo skeleton).
> **Dataset:** UCI AI4I 2020 (synthetic; results do **not** prove performance on real factory equipment).

## Documentation
| Doc | Purpose |
|---|---|
| [docs/01-scope.md](docs/01-scope.md) | One-page scope, boundaries, success criteria |
| [docs/02-user-stories.md](docs/02-user-stories.md) | User stories + acceptance criteria |
| [docs/03-data-schema.md](docs/03-data-schema.md) | Measurement schema, prediction outputs, alert rules |
| [docs/04-architecture.md](docs/04-architecture.md) | Architecture sketch, data flow, DB model |
| [docs/05-issue-board.md](docs/05-issue-board.md) | Backlog for Days 2-15 (+ `scripts/create_issues.sh`) |

## Repository layout
```
backend/    FastAPI app (api, core, db, schemas, services), Alembic, tests
ml/         preprocessing, training, evaluation code and tests
models/     saved pipelines (git-ignored artifacts)
data/       raw/ and processed/ (git-ignored, see dataset card on Day 2)
notebooks/  EDA and data-quality notebook
frontend/   React (or lightweight dashboard) app
scripts/    simulator / CSV replay, issue creation
docs/       scope, stories, schema, architecture, issue board
```

## Setup (to be completed as modules land)
```bash
git init && git add . && git commit -m "chore: Day 1 scaffold"
git branch -M main
git remote add origin <your-repo-url> && git push -u origin main
cp .env.example .env
```
Backend, ML, and frontend run instructions are added on Days 6, 3 and 11 respectively.

## Model limitations (living section)
- Trained on synthetic data; not validated on real equipment.
- Scores are decision-support signals, not failure guarantees.
- Explanations show correlated features, not causal proof.
- No Remaining Useful Life (RUL) estimation.
