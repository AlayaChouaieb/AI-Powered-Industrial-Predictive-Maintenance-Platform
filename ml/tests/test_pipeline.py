import json
import numpy as np
import pandas as pd
import pytest
from pm_ml import config as C
from pm_ml.data import content_sha256, load_clean, validate
from pm_ml.pipelines import make_preprocessor
from pm_ml.predict import Predictor, ValidationError
from pm_ml.split import load_split

pytestmark = pytest.mark.skipif(not C.RAW_CSV.exists(), reason="dataset not downloaded")

GOOD = {"product_type": "M", "air_temperature_k": 298.1, "process_temperature_k": 308.6,
        "rotational_speed_rpm": 1551, "torque_nm": 42.8, "tool_wear_min": 108}


@pytest.fixture(scope="module")
def predictor():
    return Predictor()


def test_dataset_checks_pass():
    assert all(ok for ok, _ in validate(load_clean()).values())


def test_split_disjoint_complete_and_stable():
    tr, va, te = load_split()
    ids = [set(x["udi"]) for x in (tr, va, te)]
    assert not (ids[0] & ids[1]) and not (ids[0] & ids[2]) and not (ids[1] & ids[2])
    assert len(ids[0] | ids[1] | ids[2]) == 10000
    assert (len(tr), len(va), len(te)) == (6000, 2000, 2000)
    meta = json.loads(C.SPLIT_JSON.read_text())
    assert meta["dataset_content_sha256"] == content_sha256()  # split belongs to this exact data file


def test_split_is_stratified():
    tr, va, te = load_split()
    for part in (va, te):
        for c in C.FAILURE_CLASSES:
            assert abs((part.fault_class == c).sum() - (tr.fault_class == c).sum() / 3) <= 2


@pytest.mark.parametrize("fs", ["raw", "engineered"])
def test_preprocessing_fit_on_train_only(fs):
    tr, va, _ = load_split()
    prep = make_preprocessor(fs).fit(tr[C.INPUT_COLUMNS])
    scaler = prep.named_steps["columns"].named_transformers_["num"]
    assert scaler.mean_[0] == pytest.approx(tr["air_temperature_k"].mean())
    full = pd.concat([tr, va])["air_temperature_k"].mean()
    assert scaler.mean_[0] != pytest.approx(full, abs=1e-9)


def test_labels_are_not_in_inputs():
    leak = set(C.INPUT_COLUMNS) & {"machine_failure", "TWF", "HDF", "PWF", "OSF", "RNF", "fault_class", "udi", "product_id"}
    assert not leak


def test_output_shape_and_probabilities(predictor):
    out = predictor.predict(GOOD)
    assert set(out) >= {"anomaly", "failure_risk", "fault", "status", "model_version"}
    probs = out["fault"]["probabilities"]
    assert list(probs) == C.CLASSES
    assert sum(probs.values()) == pytest.approx(1.0, abs=1e-6)
    assert out["status"] in {"healthy", "warning", "critical"}
    assert 0 <= out["failure_risk"] <= 1


def test_repeatable_and_key_order_independent(predictor):
    a = predictor.predict(GOOD)
    shuffled = dict(reversed(list(GOOD.items())))
    b = predictor.predict(shuffled)
    assert a == b


def test_batch_equals_single(predictor):
    rows = [GOOD, dict(GOOD, torque_nm=60.0, tool_wear_min=210)]
    batch = predictor.predict_batch(rows)
    assert batch[1] == predictor.predict(rows[1])


@pytest.mark.parametrize("bad", [
    {k: v for k, v in GOOD.items() if k != "torque_nm"},
    dict(GOOD, product_type="X"),
    dict(GOOD, torque_nm=-5),
    dict(GOOD, rotational_speed_rpm=0),
    dict(GOOD, air_temperature_k=float("nan")),
    dict(GOOD, tool_wear_min="abc"),
    dict(GOOD, torque_nm=None),
])
def test_invalid_payloads_rejected(predictor, bad):
    with pytest.raises(ValidationError):
        predictor.predict(bad)


def test_documented_hdf_rule_rows_are_flagged_on_validation_rows(predictor):
    _, va, _ = load_split()
    hdf = va[(va.process_temperature_k - va.air_temperature_k < 8.6) & (va.rotational_speed_rpm < 1380)]
    assert len(hdf) >= 10
    res = predictor.predict_batch(hdf[C.INPUT_COLUMNS].to_dict("records"))
    assert np.mean([r["failure_risk"] > 0.5 for r in res]) >= 0.8
