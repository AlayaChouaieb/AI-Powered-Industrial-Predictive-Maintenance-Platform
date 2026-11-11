#!/usr/bin/env bash
# Usage: gh auth login && ./scripts/create_issues.sh
set -euo pipefail
for m in "Week 1" "Week 2" "Week 3"; do
  gh api repos/:owner/:repo/milestones -f title="$m" >/dev/null 2>&1 || true
done
mk() { gh issue create --title "Day $1: $2" --milestone "$3" --body "Deliverable: $4

See docs/05-issue-board.md and the roadmap for tasks."; }
mk 2  "Select and inspect AI4I data"                "Week 1" "Dataset card and data-quality notebook"
mk 3  "Reproducible preprocessing pipeline"         "Week 1" "Pipeline and fixed stratified test split"
mk 4  "Train fault-classification baselines"        "Week 1" "Classifier, evaluation report, saved model"
mk 5  "Anomaly detection and Week 1 review (gate)"  "Week 1" "Anomaly model, metrics, Week 1 demo"
mk 6  "FastAPI skeleton and schemas"                "Week 2" "Running API with documented schemas"
mk 7  "Database and core endpoints"                 "Week 2" "Machine and measurement APIs with Alembic"
mk 8  "Integrate ML models"                         "Week 2" "Inference endpoint with tests"
mk 9  "Alerts and history"                          "Week 2" "End-to-end ingestion to alert flow"
mk 10 "Backend validation and seeded demo data"     "Week 2" "Tested backend, reproducible API demo"
mk 11 "Dashboard foundation"                        "Week 3" "Overview page on live API data"
mk 12 "Machine detail and prediction views"         "Week 3" "Trends and AI result views"
mk 13 "Alert workflow and explainability"           "Week 3" "Ack/resolve flow, feature explanation"
mk 14 "End-to-end testing and deployment"           "Week 3" "Stable demo deployment, test checklist"
mk 15 "Final evaluation and presentation"           "Week 3" "Final report, slides, demo"
