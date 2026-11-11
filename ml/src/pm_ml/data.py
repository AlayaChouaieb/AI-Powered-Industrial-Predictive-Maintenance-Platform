"""Loading, validation and label construction for AI4I 2020."""
import hashlib
import numpy as np
import pandas as pd
from . import config as C

EXPECTED = {
    "rows": 10000,
    "machine_failure": 339,
    "TWF": 46, "HDF": 115, "PWF": 95, "OSF": 98, "RNF": 19,
}


def sha256(path=C.RAW_CSV) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def content_sha256(path=C.RAW_CSV) -> str:
    """Hash of the CSV text normalised for BOM / line endings, so a fresh UCI download matches."""
    text = open(path, "rb").read().decode("utf-8-sig")
    norm = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def load_raw(path=C.RAW_CSV) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def make_fault_class(df: pd.DataFrame) -> pd.Series:
    """Single-label fault class.

    none  : machine_failure == 0 (includes 18 rows that carry only the RNF flag)
    TWF/HDF/PWF/OSF : exactly one of those four modes flagged
    other : failure with no flagged mode (9 rows) or 2+ modes at once (24 rows)
    """
    four = df[["TWF", "HDF", "PWF", "OSF"]]
    n4 = four.sum(axis=1)
    label = pd.Series("other", index=df.index)
    label[df["machine_failure"] == 0] = "none"
    single = (df["machine_failure"] == 1) & (n4 == 1) & (df["RNF"] == 0)
    for m in ["TWF", "HDF", "PWF", "OSF"]:
        label[single & (df[m] == 1)] = m
    return label


def load_clean() -> pd.DataFrame:
    df = load_raw().rename(columns=C.RENAME)
    df["fault_class"] = make_fault_class(df)
    return df


def validate(df: pd.DataFrame) -> dict:
    """Return a dict of check name -> (ok, detail). Raises nothing; caller decides."""
    out = {}
    out["row_count"] = (len(df) == EXPECTED["rows"], len(df))
    out["no_missing"] = (int(df[C.INPUT_COLUMNS].isna().sum().sum()) == 0, int(df.isna().sum().sum()))
    out["no_duplicate_rows"] = (int(df.drop(columns=["udi"]).duplicated().sum()) == 0,
                                int(df.drop(columns=["udi"]).duplicated().sum()))
    out["udi_unique"] = (df["udi"].is_unique, None)
    out["types_valid"] = (set(df["product_type"]) <= set(C.PRODUCT_TYPES), sorted(df["product_type"].unique()))
    for k in ["machine_failure"] + C.MODE_COLS:
        s = int(df[k].sum())
        out[f"count_{k}"] = (s == EXPECTED[k], s)
    for col, (lo, hi) in C.VALID_RANGES.items():
        out[f"range_{col}"] = (bool(df[col].between(lo, hi).all()), (float(df[col].min()), float(df[col].max())))
    return out


if __name__ == "__main__":
    d = load_clean()
    print("sha256:", sha256())
    for k, (ok, detail) in validate(d).items():
        print(("OK  " if ok else "FAIL"), k, detail)
    print(d["fault_class"].value_counts())
