"""Orchestrates Days 4-5: trains, selects, thresholds, saves frozen artifacts + report tables/figures.
Uses train + validation only. The test split is never loaded into any computation here."""
import json
import platform
import joblib
import numpy as np
import pandas as pd
import sklearn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.inspection import permutation_importance
from sklearn.metrics import precision_recall_curve, f1_score

from . import __version__, config as C
from .data import content_sha256, sha256
from .evaluate import classification_summary, precision_recall_at_thresholds
from .policy import health_status
from .train_anomaly import CHOSEN_FAR, evaluate_scores, tradeoff_table, main as anomaly_main
from .train_classifier import main as classifier_main, reorder_proba


def save_cm(cm, title, path):
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(C.CLASSES)), C.CLASSES); ax.set_yticks(range(len(C.CLASSES)), C.CLASSES)
    ax.set_xlabel("Predicted"); ax.set_ylabel("True"); ax.set_title(title, fontsize=10)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def main():
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)
    C.MODEL_DIR.mkdir(exist_ok=True)
    res, store, best, (train, val) = classifier_main()
    ytr, yva = train["fault_class"].values, val["fault_class"].values
    sel = store[best]
    # ---- classifier tables / figures
    sel["cv_pc"].round(4).to_csv(C.REPORT_DIR / "classifier_per_class_cv.csv")
    sel["va_pc"].round(4).to_csv(C.REPORT_DIR / "classifier_per_class_val.csv")
    pd.DataFrame(sel["cv_cm"], index=C.CLASSES, columns=C.CLASSES).to_csv(C.REPORT_DIR / "confusion_cv.csv")
    pd.DataFrame(sel["va_cm"], index=C.CLASSES, columns=C.CLASSES).to_csv(C.REPORT_DIR / "confusion_val.csv")
    save_cm(sel["cv_cm"], f"{best}: 5-fold CV on train (n={len(train)})", C.FIG_DIR / "confusion_cv.png")
    save_cm(sel["va_cm"], f"{best}: validation (n={len(val)})", C.FIG_DIR / "confusion_val.png")

    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    yb = (ytr != "none").astype(int)
    for name, d in store.items():
        pf = 1 - d["oof"][:, C.CLASSES.index("none")]
        pr, rc, _ = precision_recall_curve(yb, pf)
        ax.plot(rc, pr, label=name, lw=2 if name == best else 1)
    ax.axhline(yb.mean(), color="gray", ls=":", label=f"base rate {yb.mean():.3f}")
    ax.set_xlabel("Recall"); ax.set_ylabel("Precision"); ax.set_title("Any-failure PR curves (CV out-of-fold, train)", fontsize=10)
    ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(C.FIG_DIR / "pr_curves_cv.png", dpi=130); plt.close(fig)

    # permutation importance on validation, in terms of the raw API inputs
    pipe = sel["pipe"]
    pi = permutation_importance(pipe, val[C.INPUT_COLUMNS], yva, scoring="f1_macro",
                                n_repeats=10, random_state=C.SEED, n_jobs=-1)
    imp = pd.DataFrame({"feature": C.INPUT_COLUMNS, "mean_drop_macro_f1": pi.importances_mean,
                        "std": pi.importances_std}).sort_values("mean_drop_macro_f1", ascending=False)
    imp.round(4).to_csv(C.REPORT_DIR / "permutation_importance_val.csv", index=False)
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.barh(imp["feature"][::-1], imp["mean_drop_macro_f1"][::-1], xerr=imp["std"][::-1])
    ax.set_xlabel("Drop in validation macro-F1 when shuffled"); ax.set_title("Permutation importance (API inputs)", fontsize=10)
    fig.tight_layout(); fig.savefig(C.FIG_DIR / "permutation_importance.png", dpi=130); plt.close(fig)

    # ---- classifier-risk thresholds from train OOF (rule fixed in advance)
    pf_oof = 1 - sel["oof"][:, C.CLASSES.index("none")]
    yb_tr = (ytr != "none").astype(int)
    grid = np.unique(np.round(np.concatenate([np.linspace(0.05, 0.95, 19), pf_oof[pf_oof > 0]]), 4))
    tab = precision_recall_at_thresholds(yb_tr, pf_oof, grid)
    p_crit = float(tab[tab["precision"] >= 0.90]["threshold"].min())
    p_warn = float(tab[tab["precision"] >= 0.60]["threshold"].min())
    p_warn = min(p_warn, p_crit)
    pf_val = 1 - sel["pva"][:, C.CLASSES.index("none")]
    yb_va = (yva != "none").astype(int)
    pts = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    pd.concat({"train_oof": precision_recall_at_thresholds(yb_tr, pf_oof, pts),
               "val": precision_recall_at_thresholds(yb_va, pf_val, pts)}).round(3).to_csv(
        C.REPORT_DIR / "risk_threshold_table.csv")

    # ---- anomaly detector
    ares, afit, ascores, abest = anomaly_main(train, val)
    ares.round(4).to_csv(C.REPORT_DIR / "anomaly_results.csv")
    for fs in ascores:
        tradeoff_table(val, ascores[fs]).round(4).to_csv(C.REPORT_DIR / f"anomaly_tradeoff_{fs}.csv")
    a_thr = float(ares.loc[abest, "threshold"])
    s = ascores[abest]
    normal = (yva == "none")
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    ax[0].hist(s[normal], bins=40, alpha=.6, density=True, label="normal (val)")
    ax[0].hist(s[~normal], bins=40, alpha=.6, density=True, label="failure (val)")
    ax[0].axvline(a_thr, color="k", ls="--", label=f"threshold ({CHOSEN_FAR:.0%} false-alarm budget)")
    ax[0].set_xlabel("Anomaly score (higher = more unusual)"); ax[0].legend(fontsize=7)
    ax[0].set_title(f"Isolation Forest ({abest} features)", fontsize=10)
    tt = tradeoff_table(val, s)
    ax[1].plot(tt["false_alarm_rate"], tt["recall_any_failure"], "o-", label="recall of failures")
    ax[1].plot(tt["false_alarm_rate"], tt["precision"], "s-", label="precision")
    ax[1].set_xlabel("False-alarm rate on normal rows"); ax[1].legend(fontsize=8); ax[1].set_title("Threshold trade-off (val)", fontsize=10)
    fig.tight_layout(); fig.savefig(C.FIG_DIR / "anomaly_scores.png", dpi=130); plt.close(fig)

    # false alarms / missed
    v = val.copy(); v["anomaly_score"] = s; v["flag"] = s >= a_thr
    fa = v[(v.fault_class == "none") & v.flag].sort_values("anomaly_score", ascending=False)
    miss = v[(v.fault_class != "none") & ~v.flag].sort_values("anomaly_score", ascending=False)
    cols = ["udi", "product_type"] + C.RAW_NUMERIC + ["fault_class", "anomaly_score"]
    fa[cols].round(3).to_csv(C.REPORT_DIR / "anomaly_false_alarms_val.csv", index=False)
    miss[cols].round(3).to_csv(C.REPORT_DIR / "anomaly_missed_failures_val.csv", index=False)
    prof = pd.concat({"normal_not_flagged": v[(v.fault_class == "none") & ~v.flag][C.RAW_NUMERIC].median(),
                      "false_alarms": fa[C.RAW_NUMERIC].median(),
                      "failures_caught": v[(v.fault_class != "none") & v.flag][C.RAW_NUMERIC].median(),
                      "failures_missed": miss[C.RAW_NUMERIC].median()}, axis=1)
    prof.round(2).to_csv(C.REPORT_DIR / "anomaly_review_feature_medians.csv")
    miss_by = (miss.fault_class.value_counts().rename("missed")
               .to_frame().join(v[v.fault_class != "none"].fault_class.value_counts().rename("total")))
    miss_by.to_csv(C.REPORT_DIR / "anomaly_missed_by_class.csv")

    # ---- combined status policy on validation
    th = {"anomaly": {"threshold": a_thr, "far_budget": CHOSEN_FAR, "feature_set": abest,
                      "score_definition": "-IsolationForest.score_samples (higher = more unusual)",
                      "threshold_rule": "95th percentile of validation NORMAL rows' scores"},
          "classifier": {"p_warn": p_warn, "p_crit": p_crit,
                         "p_fail_definition": "1 - P(none)",
                         "rule": "p_crit = lowest risk threshold with train-OOF precision >= 0.90; "
                                 "p_warn = lowest risk threshold with train-OOF precision >= 0.60 "
                                 "(first attempt used recall>=0.85, which collapsed onto p_crit)"}}
    status = [health_status(pf, sc, th) for pf, sc in zip(pf_val, s)]
    sdf = pd.DataFrame({"status": status, "failure": yb_va})
    stab = sdf.groupby("status").agg(rows=("failure", "size"), failures=("failure", "sum"))
    stab["failure_rate"] = stab["failures"] / stab["rows"]
    stab = stab.reindex(["healthy", "warning", "critical"]).fillna(0)
    stab.round(4).to_csv(C.REPORT_DIR / "status_policy_val.csv")

    # binary comparison classifier vs anomaly at chosen settings (val)
    cmp = pd.DataFrame({
        "classifier_any_failure": [float(((pf_val >= 0.5) & (yb_va == 1)).sum() / max((pf_val >= 0.5).sum(), 1)),
                                   float(((pf_val >= 0.5) & (yb_va == 1)).sum() / yb_va.sum())],
        "anomaly_detector": [ares.loc[abest, "precision"], ares.loc[abest, "recall_any_failure"]],
    }, index=["precision", "recall"])
    cmp.round(3).to_csv(C.REPORT_DIR / "classifier_vs_anomaly_val.csv")

    # ---- freeze artifacts
    joblib.dump(pipe, C.MODEL_DIR / "classifier.joblib", compress=3)
    joblib.dump(afit[abest], C.MODEL_DIR / "anomaly.joblib", compress=3)
    (C.MODEL_DIR / "thresholds.json").write_text(json.dumps(th, indent=2))
    fcfg = {"input_columns": C.INPUT_COLUMNS, "product_types": C.PRODUCT_TYPES,
            "classes_order": C.CLASSES, "classifier_model_class_order": list(pipe.named_steps["model"].classes_),
            "classifier_feature_set": best, "anomaly_feature_set": abest,
            "valid_ranges": C.VALID_RANGES, "engineered_features": C.ENGINEERED}
    (C.MODEL_DIR / "feature_config.json").write_text(json.dumps(fcfg, indent=2))
    (C.MODEL_DIR / "model_card.json").write_text(json.dumps({
        "model_version": __version__, "classifier": best, "anomaly_detector": f"isolation-forest-{abest}",
        "trained_on": "train split only (60%); validation used for model/threshold selection; test split untouched",
        "dataset_file_sha256": sha256(), "dataset_content_sha256": content_sha256(), "seed": C.SEED,
        "sklearn": sklearn.__version__, "python": platform.python_version(),
        "classifier_cv_summary": {k: round(float(v), 4) for k, v in res.set_index("model").loc[best].items()
                                  if k.startswith("cv_")},
        "classifier_val_summary": {k: round(float(v), 4) for k, v in res.set_index("model").loc[best].items()
                                   if k.startswith("val_")},
        "anomaly_val_summary": {k: (round(float(v), 4) if v == v else None) for k, v in ares.loc[abest].items()},
        "supported_fault_classes": ["HDF", "PWF", "OSF"],
        "unsupported_fault_classes": {"TWF": "no usable signal beyond high tool wear (CV recall 0)",
                                      "other": "too few and heterogeneous examples (19 in train)"},
        "limitations": ["synthetic data", "failure labels (HDF/PWF/OSF) are deterministic rules of the inputs",
                        "very few examples of TWF/other", "no real machine IDs or time ordering"],
    }, indent=2))
    print("best classifier:", best, "| anomaly:", abest)
    print("thresholds:", json.dumps(th, indent=1))
    print(stab)
    print(cmp)
    print(imp)
    print(miss_by)
    print(prof)
    print(sel["va_pc"].round(3)); print(sel["cv_pc"].round(3))
    print(pd.DataFrame(sel["cv_cm"], index=C.CLASSES, columns=C.CLASSES))
    print(pd.DataFrame(sel["va_cm"], index=C.CLASSES, columns=C.CLASSES))
    print(tab[tab.threshold.isin([p_warn, p_crit])])


if __name__ == "__main__":
    main()
