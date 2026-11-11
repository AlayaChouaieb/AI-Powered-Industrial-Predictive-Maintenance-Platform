"""Explicit health-status rules combining classifier risk and anomaly flag (thresholds in models/thresholds.json)."""


def failure_probability(proba_none: float) -> float:
    return 1.0 - float(proba_none)


def health_status(p_fail: float, anomaly_score: float, th: dict) -> str:
    """critical: classifier risk >= p_crit
    warning : classifier risk >= p_warn, or anomaly score >= threshold
    healthy : otherwise"""
    if p_fail >= th["classifier"]["p_crit"]:
        return "critical"
    if p_fail >= th["classifier"]["p_warn"] or anomaly_score >= th["anomaly"]["threshold"]:
        return "warning"
    return "healthy"
