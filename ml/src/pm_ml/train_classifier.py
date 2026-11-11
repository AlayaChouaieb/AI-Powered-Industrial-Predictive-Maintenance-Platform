"""Day 4: train and compare classifier baselines (train split only; test split untouched)."""
import json
import time
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from . import __version__
from . import config as C
from .data import sha256
from .evaluate import classification_summary
from .pipelines import make_classifier
from .split import load_split

CONFIGS = [
    ("logreg", "raw", {"C": 1.0}),
    ("logreg", "engineered", {"C": 1.0}),
    ("rf", "raw", {"n_estimators": 300, "min_samples_leaf": 2}),
    ("rf", "engineered", {"n_estimators": 300, "min_samples_leaf": 2}),
    ("rf", "engineered", {"n_estimators": 300, "min_samples_leaf": 1}),
    ("rf", "engineered", {"n_estimators": 300, "min_samples_leaf": 5}),
]


def reorder_proba(model, proba):
    """Return proba columns in C.CLASSES order."""
    cls = list(model.classes_)
    return proba[:, [cls.index(c) for c in C.CLASSES]]


def main():
    train, val, _test = load_split()  # test split is NOT loaded into any computation
    Xtr, ytr = train[C.INPUT_COLUMNS], train["fault_class"].values
    Xva, yva = val[C.INPUT_COLUMNS], val["fault_class"].values
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=C.SEED)
    rows, store = [], {}
    for kind, fs, params in CONFIGS:
        name = f"{kind}-{fs}" + (f"-leaf{params['min_samples_leaf']}" if kind == "rf" else "")
        t0 = time.time()
        pipe = make_classifier(kind, fs, **params)
        oof = cross_val_predict(pipe, Xtr, ytr, cv=cv, method="predict_proba")
        # cross_val_predict orders columns by sorted class names
        srt = sorted(C.CLASSES)
        oof = oof[:, [srt.index(c) for c in C.CLASSES]]
        cv_s, cv_pc, cv_cm = classification_summary(ytr, oof)
        pipe.fit(Xtr, ytr)
        pva = reorder_proba(pipe.named_steps["model"], pipe.predict_proba(Xva))
        va_s, va_pc, va_cm = classification_summary(yva, pva)
        row = {"model": name, "params": json.dumps(params), "fit_seconds": round(time.time() - t0, 1)}
        row.update({f"cv_{k}": v for k, v in cv_s.items()})
        row.update({f"val_{k}": v for k, v in va_s.items()})
        rows.append(row)
        store[name] = dict(pipe=pipe, oof=oof, cv_pc=cv_pc, cv_cm=cv_cm, pva=pva, va_pc=va_pc, va_cm=va_cm)
        print(name, {k: round(v, 3) for k, v in cv_s.items()})
    res = pd.DataFrame(rows)
    # Selection rule fixed in advance: highest CV macro PR-AUC over the 5 failure classes
    best = res.sort_values("cv_macro_pr_auc_failure_classes", ascending=False).iloc[0]["model"]
    res["selected"] = res["model"] == best
    C.REPORT_DIR.mkdir(exist_ok=True)
    res.to_csv(C.REPORT_DIR / "classifier_results.csv", index=False)
    print("selected:", best)
    return res, store, best, (train, val)


if __name__ == "__main__":
    main()
