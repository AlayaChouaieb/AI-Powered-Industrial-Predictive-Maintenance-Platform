"""Day 5: Isolation Forest trained on NORMAL training rows only; threshold chosen on validation data."""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from . import config as C
from .pipelines import anomaly_score, make_anomaly

FAR_BUDGETS = [0.01, 0.02, 0.05, 0.10, 0.20]
CHOSEN_FAR = 0.05


def evaluate_scores(val: pd.DataFrame, scores: np.ndarray, threshold: float) -> dict:
    y = (val["fault_class"] != "none").values
    flag = scores >= threshold
    normal = ~y
    out = {
        "roc_auc": float(roc_auc_score(y, scores)),
        "pr_auc": float(average_precision_score(y, scores)),
        "threshold": float(threshold),
        "false_alarm_rate": float(flag[normal].mean()),
        "recall_any_failure": float(flag[y].mean()),
        "precision": float(flag[y].sum() / max(flag.sum(), 1)),
        "flagged": int(flag.sum()),
    }
    for c in C.FAILURE_CLASSES:
        m = (val["fault_class"] == c).values
        out[f"recall_{c}"] = float(flag[m].mean()) if m.any() else np.nan
    return out


def tradeoff_table(val: pd.DataFrame, scores: np.ndarray) -> pd.DataFrame:
    normal_scores = scores[(val["fault_class"] == "none").values]
    rows = []
    for far in FAR_BUDGETS:
        t = np.quantile(normal_scores, 1 - far)
        r = evaluate_scores(val, scores, t)
        r["far_budget"] = far
        rows.append(r)
    return pd.DataFrame(rows).set_index("far_budget")


def main(train: pd.DataFrame, val: pd.DataFrame):
    normal_train = train[train["fault_class"] == "none"]
    res, fitted, scores = [], {}, {}
    for fs in ["raw", "engineered"]:
        pipe = make_anomaly(fs).fit(normal_train[C.INPUT_COLUMNS])
        s = anomaly_score(pipe, val[C.INPUT_COLUMNS])
        thr = np.quantile(s[(val["fault_class"] == "none").values], 1 - CHOSEN_FAR)
        r = evaluate_scores(val, s, thr)
        r["feature_set"] = fs
        res.append(r)
        fitted[fs], scores[fs] = pipe, s
    res = pd.DataFrame(res).set_index("feature_set")
    best = res["pr_auc"].idxmax()  # selection rule: validation PR-AUC vs failure labels (imperfect proxy)
    return res, fitted, scores, best
