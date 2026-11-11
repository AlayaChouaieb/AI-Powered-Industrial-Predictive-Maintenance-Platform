"""Inference service logic: validate -> features -> anomaly + classifier -> status.
Loaded once at startup by the API (Day 8). Feature order is fixed by models/feature_config.json."""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from . import __version__, config as C
from .policy import failure_probability, health_status


class ValidationError(ValueError):
    pass


class Predictor:
    def __init__(self, model_dir=C.MODEL_DIR):
        d = Path(model_dir)
        self.classifier = joblib.load(d / "classifier.joblib")
        self.anomaly = joblib.load(d / "anomaly.joblib")
        self.th = json.loads((d / "thresholds.json").read_text())
        self.cfg = json.loads((d / "feature_config.json").read_text())
        self.card = json.loads((d / "model_card.json").read_text())
        self.input_columns = self.cfg["input_columns"]
        self._order = [self.cfg["classifier_model_class_order"].index(c) for c in self.cfg["classes_order"]]

    # ---- validation
    def validate(self, payload: dict) -> dict:
        missing = [c for c in self.input_columns if c not in payload or payload[c] is None]
        if missing:
            raise ValidationError(f"missing fields: {missing}")
        if payload["product_type"] not in self.cfg["product_types"]:
            raise ValidationError(f"product_type must be one of {self.cfg['product_types']}")
        clean = {"product_type": payload["product_type"]}
        for col, (lo, hi) in self.cfg["valid_ranges"].items():
            try:
                v = float(payload[col])
            except (TypeError, ValueError):
                raise ValidationError(f"{col} must be a number")
            if not np.isfinite(v) or not (lo <= v <= hi):
                raise ValidationError(f"{col}={payload[col]} outside valid range [{lo}, {hi}]")
            clean[col] = v
        return clean

    # ---- prediction
    def predict_batch(self, payloads: list) -> list:
        rows = [self.validate(p) for p in payloads]
        X = pd.DataFrame(rows, columns=self.input_columns)  # fixed column order
        proba = self.classifier.predict_proba(X)[:, self._order]
        score = -self.anomaly.score_samples(X)
        out = []
        for i in range(len(X)):
            probs = {c: float(proba[i, j]) for j, c in enumerate(self.cfg["classes_order"])}
            p_fail = failure_probability(probs["none"])
            supported = [c for c in C.FAILURE_CLASSES if c in self.card.get("supported_fault_classes", [])]
            best = max(supported, key=lambda c: probs[c]) if supported else None
            out.append({
                "anomaly": {"score": float(score[i]), "threshold": self.th["anomaly"]["threshold"],
                            "is_anomaly": bool(score[i] >= self.th["anomaly"]["threshold"])},
                "failure_risk": p_fail,
                "fault": {"predicted_class": max(probs, key=probs.get), "probabilities": probs,
                          "most_likely_failure_mode": best,
                          "supported_modes": supported},
                "status": health_status(p_fail, float(score[i]), self.th),
                "top_factors": [],  # Day 13 (local explanations)
                "model_version": self.card["model_version"],
                "note": "Decision-support signal from a model trained on synthetic data; not a failure guarantee.",
            })
        return out

    def predict(self, payload: dict) -> dict:
        return self.predict_batch([payload])[0]
