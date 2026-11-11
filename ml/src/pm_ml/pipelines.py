"""Model pipelines. All preprocessing lives INSIDE the pipeline so it is fit on training data only."""
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from . import config as C
from .features import add_engineered


def numeric_columns(feature_set: str):
    if feature_set == "raw":
        return list(C.RAW_NUMERIC)
    if feature_set == "engineered":
        return list(C.RAW_NUMERIC) + list(C.ENGINEERED)
    raise ValueError(feature_set)


def make_preprocessor(feature_set: str, scale: bool = True) -> Pipeline:
    """Raw input frame (INPUT_COLUMNS) -> numeric matrix."""
    num = numeric_columns(feature_set)
    num_tf = StandardScaler() if scale else "passthrough"
    ct = ColumnTransformer(
        [("num", num_tf, num),
         ("cat", OneHotEncoder(categories=[C.PRODUCT_TYPES], handle_unknown="error"), C.CATEGORICAL)],
        verbose_feature_names_out=False,
    )
    steps = []
    if feature_set == "engineered":
        steps.append(("engineer", FunctionTransformer(add_engineered, validate=False)))
    steps.append(("columns", ct))
    return Pipeline(steps)


def make_classifier(kind: str, feature_set: str, seed: int = C.SEED, **params) -> Pipeline:
    if kind == "logreg":
        est = LogisticRegression(C=params.get("C", 1.0), class_weight="balanced",
                                 max_iter=2000, random_state=seed)
        scale = True
    elif kind == "rf":
        est = RandomForestClassifier(
            n_estimators=params.get("n_estimators", 300),
            min_samples_leaf=params.get("min_samples_leaf", 2),
            max_depth=params.get("max_depth", None),
            class_weight="balanced_subsample", n_jobs=-1, random_state=seed)
        scale = False
    else:
        raise ValueError(kind)
    return Pipeline([("prep", make_preprocessor(feature_set, scale)), ("model", est)])


def make_anomaly(feature_set: str, seed: int = C.SEED, **params) -> Pipeline:
    est = IsolationForest(n_estimators=params.get("n_estimators", 300),
                          max_samples=params.get("max_samples", "auto"),
                          contamination="auto", random_state=seed, n_jobs=-1)
    return Pipeline([("prep", make_preprocessor(feature_set, scale=False)), ("model", est)])


def anomaly_score(pipe: Pipeline, X):
    """Higher = more unusual."""
    return -pipe.score_samples(X)
