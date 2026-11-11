# AI-Powered Industrial Predictive Maintenance Platform

A 3-week prototype web platform that ingests machine measurements, runs **anomaly detection** and **fault classification**, stores results, and shows alerts to a maintenance user.

> **Status:** Week 1 complete (Days 1-5): data audit, preprocessing + fixed split, fault classifier, anomaly detector, frozen model artifacts. Week 2 (backend) is next.
> **Dataset:** UCI AI4I 2020 (synthetic; results do **not** prove performance on real factory equipment).

## Documentation
| Doc | Purpose |
|---|---|
| [docs/01-scope.md](docs/01-scope.md) | One-page scope, boundaries, success criteria |
| [docs/02-user-stories.md](docs/02-user-stories.md) | User stories + acceptance criteria |
| [docs/03-data-schema.md](docs/03-data-schema.md) | Measurement schema, prediction outputs, alert rules |
| [docs/04-architecture.md](docs/04-architecture.md) | Architecture sketch, data flow, DB model |
| [docs/05-issue-board.md](docs/05-issue-board.md) | Backlog for Days 2-15 (+ `scripts/create_issues.sh`) |
| [docs/dataset-card.md](docs/dataset-card.md) | Dataset card: source, columns, labels, known issues |
| [docs/06-week1-report.md](docs/06-week1-report.md) | **Week 1 report: metrics, thresholds, feasibility gate, limitations** |
| [notebooks/01_data_quality.ipynb](notebooks/01_data_quality.ipynb) | Data-quality notebook (HTML copy in `reports/`) |

## Repository layout
```
backend/    FastAPI app (api, core, db, schemas, services), Alembic, tests
ml/         preprocessing, training, evaluation code and tests
models/     frozen classifier, anomaly detector, thresholds, feature config, model card
reports/    metrics tables, figures, demo output
data/       raw/ and processed/ (git-ignored, see dataset card on Day 2)
notebooks/  EDA and data-quality notebook
frontend/   React (or lightweight dashboard) app
scripts/    simulator / CSV replay, issue creation
docs/       scope, stories, schema, architecture, issue board
```

## Quick start (ML part)
```bash
pip install -r ml/requirements.txt
cd ml/src && python -m pm_ml.download_data     # or put ai4i2020.csv in data/raw/
python -m pm_ml.run_week1                      # retrain + regenerate models/ and reports/
cd ../.. && python -m pytest ml -q             # 17 tests
python scripts/week1_demo.py                   # score sample measurements
```

## Week 1 results snapshot (validation / cross-validation, test set untouched)
- Any-failure risk: out-of-fold PR-AUC 0.90 (base rate 0.034).
- Fault modes: HDF / PWF / OSF supported (CV F1 0.87 / 0.93 / 0.93); TWF **not** predictable; `other` weak.
- Anomaly detector (Isolation Forest): weak failure proxy (41% recall at 22% precision, 5% false-alarm budget).
- Caveat: HDF/PWF/OSF labels are deterministic rules of the inputs, so scores overstate real-world performance.

## Model limitations (living section)
- Trained on synthetic data; not validated on real equipment.
- Scores are decision-support signals, not failure guarantees.
- Explanations show correlated features, not causal proof.
- No Remaining Useful Life (RUL) estimation.
