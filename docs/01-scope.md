# 01 - Project Scope (one page)

## Objective
Build a working prototype that lets a maintenance user monitor machines, see whether a machine behaves unusually, see a likely fault category, and acknowledge/resolve alerts. Data comes from CSV replay or a small simulator; no hardware.

## Target asset family
General industrial equipment / rotating machinery, represented by **UCI AI4I 2020** (air/process temperature, rotational speed, torque, tool wear, failure labels).

## Two AI functions
1. **Anomaly detection** (Isolation Forest): "is this measurement unusual?" -> score + status.
2. **Fault classification** (Logistic Regression baseline, Random Forest): "which known failure mode?" -> class + probabilities.

## One end-to-end workflow
Measurement in (API/CSV) -> validation -> PostgreSQL -> inference -> prediction + alert stored -> dashboard -> alert acknowledged/resolved with a note.

## In scope
- One dataset, one schema, two models, one workflow
- Saved preprocessing + model artifacts, held-out evaluation (precision, recall, F1, confusion matrix, PR-AUC)
- FastAPI + PostgreSQL + migrations, tests
- Dashboard: overview, machine detail, alert/history
- Confidence/score display, limitations, plain-language factors

## Out of scope
RUL, multiple datasets (CWRU, C-MAPSS), real-time hardware, streaming, multi-tenancy, auth/roles (future work).

## Success criteria (Definition of Done)
- Register/select a machine; submit a measurement via API or CSV
- Stored measurement returns anomaly result (+ fault class where supported)
- Predictions and alerts visible in the dashboard and persist after restart
- Metrics reported on an untouched test set; README documents setup, data source, API, limitations, demo

## Feasibility gate (end of Day 5)
A reproducible model evaluation must exist. If labels don't support a reliable classifier, narrow to anomaly detection and move classification to future work.

## Cut order if behind
SHAP -> auth/roles -> advanced charts -> Docker. Never cut: data validation, held-out evaluation, end-to-end workflow.

## Key risks
| Risk | Mitigation |
|---|---|
| Rare failure classes (esp. RNF) | Class weights, PR-AUC, class-wise metrics; may merge/exclude classes |
| AI4I has no timestamps or real machine IDs | Replay/simulator assigns timestamps and machine IDs; documented as an assumption |
| Over-claiming from synthetic data | Dataset card + README limitations |
| Frontend time overrun | Use a lightweight dashboard instead of full React |
