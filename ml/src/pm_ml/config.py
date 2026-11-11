from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW_CSV = ROOT / "data" / "raw" / "ai4i2020.csv"
SPLIT_JSON = ROOT / "data" / "processed" / "split.json"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"
FIG_DIR = REPORT_DIR / "figures"

SEED = 42
SPLIT_FRACTIONS = {"train": 0.60, "val": 0.20, "test": 0.20}

# AI4I column -> API / internal field name (see docs/03-data-schema.md)
RENAME = {
    "UDI": "udi",
    "Product ID": "product_id",
    "Type": "product_type",
    "Air temperature [K]": "air_temperature_k",
    "Process temperature [K]": "process_temperature_k",
    "Rotational speed [rpm]": "rotational_speed_rpm",
    "Torque [Nm]": "torque_nm",
    "Tool wear [min]": "tool_wear_min",
    "Machine failure": "machine_failure",
}
MODE_COLS = ["TWF", "HDF", "PWF", "OSF", "RNF"]

# Inputs available at prediction time (order matters: it is the API contract)
RAW_NUMERIC = [
    "air_temperature_k",
    "process_temperature_k",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
]
CATEGORICAL = ["product_type"]
PRODUCT_TYPES = ["L", "M", "H"]
INPUT_COLUMNS = ["product_type"] + RAW_NUMERIC

# Physics-motivated derived features (computed only from the inputs above)
ENGINEERED = ["temp_diff_k", "power_w", "strain_minnm"]

# Fault classes: none + 4 predictable modes + "other"
# other = failure flagged only as RNF, failure with no mode flagged, or 2+ modes at once
CLASSES = ["none", "TWF", "HDF", "PWF", "OSF", "other"]
FAILURE_CLASSES = CLASSES[1:]

# Valid input ranges used by API validation (derived from the data, widened; see dataset card)
VALID_RANGES = {
    "air_temperature_k": (250.0, 400.0),
    "process_temperature_k": (250.0, 450.0),
    "rotational_speed_rpm": (1.0, 10000.0),
    "torque_nm": (0.0, 500.0),
    "tool_wear_min": (0.0, 1000.0),
}
