"""Fixed, stratified train/val/test split stored as UDI lists so every run and every person uses the same rows."""
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from . import config as C
from .data import content_sha256, load_clean


def make_split(df: pd.DataFrame):
    tr_val, test = train_test_split(df, test_size=C.SPLIT_FRACTIONS["test"],
                                    stratify=df["fault_class"], random_state=C.SEED)
    rel_val = C.SPLIT_FRACTIONS["val"] / (1 - C.SPLIT_FRACTIONS["test"])
    train, val = train_test_split(tr_val, test_size=rel_val,
                                  stratify=tr_val["fault_class"], random_state=C.SEED)
    return train, val, test


def write_split():
    df = load_clean()
    train, val, test = make_split(df)
    payload = {
        "seed": C.SEED, "stratified_on": "fault_class",
        "dataset_content_sha256": content_sha256(),
        "fractions": C.SPLIT_FRACTIONS,
        "udi": {"train": sorted(map(int, train["udi"])),
                "val": sorted(map(int, val["udi"])),
                "test": sorted(map(int, test["udi"]))},
    }
    C.SPLIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    C.SPLIT_JSON.write_text(json.dumps(payload))
    return payload


def load_split(df: pd.DataFrame = None):
    """Return (train, val, test) DataFrames using the stored split."""
    df = load_clean() if df is None else df
    s = json.loads(C.SPLIT_JSON.read_text())
    idx = df.set_index("udi")
    return tuple(idx.loc[s["udi"][k]].reset_index() for k in ("train", "val", "test"))


if __name__ == "__main__":
    p = write_split()
    tr, va, te = load_split()
    print({k: len(v) for k, v in p["udi"].items()})
    print(pd.DataFrame({"train": tr.fault_class.value_counts(), "val": va.fault_class.value_counts(),
                        "test": te.fault_class.value_counts()}))
