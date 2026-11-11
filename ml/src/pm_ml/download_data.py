"""Download AI4I 2020 from UCI into data/raw/ and verify it (run once on a machine with internet access).
    python -m pm_ml.download_data
NOTE: written for the UCI static-file URL; if it changes, download ai4i2020.csv manually from
https://archive.ics.uci.edu/dataset/601 and place it in data/raw/. Verification below is the same either way."""
import io
import urllib.request
import zipfile
from . import config as C
from .data import content_sha256, load_clean, validate

URL = "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"


def main():
    C.RAW_CSV.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=60) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    name = next(n for n in z.namelist() if n.lower().endswith("ai4i2020.csv"))
    C.RAW_CSV.write_bytes(z.read(name))
    bad = {k: v for k, (ok, v) in validate(load_clean()).items() if not ok}
    print("content sha256:", content_sha256())
    print("verification:", "OK" if not bad else f"FAILED {bad}")


if __name__ == "__main__":
    main()
