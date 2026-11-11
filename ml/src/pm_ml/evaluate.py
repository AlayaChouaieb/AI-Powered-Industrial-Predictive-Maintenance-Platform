"""Metric helpers. Accuracy is deliberately not the headline: classes are very imbalanced."""
import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             precision_recall_fscore_support, roc_auc_score)
from . import config as C


def classification_summary(y_true, proba, classes=C.CLASSES):
    """y_true: array of class names; proba: (n, len(classes)) in `classes` order."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(classes)[np.asarray(proba).argmax(axis=1)]
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, labels=classes, zero_division=0)
    per_class = pd.DataFrame({"precision": p, "recall": r, "f1": f, "support": s}, index=classes)
    ap = {}
    for i, c in enumerate(classes):
        yt = (y_true == c).astype(int)
        ap[c] = average_precision_score(yt, proba[:, i]) if yt.sum() > 0 else np.nan
    per_class["pr_auc"] = pd.Series(ap)
    fail = [c for c in classes if c != "none"]
    # binary view: "any failure" score = 1 - P(none)
    p_fail = 1.0 - np.asarray(proba)[:, classes.index("none")]
    yb = (y_true != "none").astype(int)
    yb_pred = (y_pred != "none").astype(int)
    bp, br, bf, _ = precision_recall_fscore_support(yb, yb_pred, average="binary", zero_division=0)
    summary = {
        "macro_f1_failure_classes": float(per_class.loc[fail, "f1"].mean()),
        "macro_pr_auc_failure_classes": float(per_class.loc[fail, "pr_auc"].mean()),
        "binary_failure_pr_auc": float(average_precision_score(yb, p_fail)),
        "binary_failure_roc_auc": float(roc_auc_score(yb, p_fail)),
        "binary_failure_precision": float(bp),
        "binary_failure_recall": float(br),
        "binary_failure_f1": float(bf),
        "accuracy_for_reference": float((y_true == y_pred).mean()),
    }
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    return summary, per_class, cm


def precision_recall_at_thresholds(y_bin, score, thresholds):
    rows = []
    for t in thresholds:
        pred = score >= t
        tp = int((pred & (y_bin == 1)).sum()); fp = int((pred & (y_bin == 0)).sum())
        fn = int((~pred & (y_bin == 1)).sum())
        rows.append({"threshold": float(t),
                     "precision": tp / (tp + fp) if tp + fp else np.nan,
                     "recall": tp / (tp + fn) if tp + fn else np.nan,
                     "flagged": int(pred.sum()), "tp": tp, "fp": fp, "fn": fn})
    return pd.DataFrame(rows)
