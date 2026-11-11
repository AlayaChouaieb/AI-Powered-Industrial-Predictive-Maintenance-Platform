# Dataset Card: UCI AI4I 2020 Predictive Maintenance Dataset

## Summary
| | |
|---|---|
| Source | UCI Machine Learning Repository, dataset 601 (https://archive.ics.uci.edu/dataset/601) |
| DOI | 10.24432/C5HS5C |
| License | CC BY 4.0 (attribution required) |
| Author / paper | S. Matzka, "Explainable Artificial Intelligence for Predictive Maintenance Applications," 2020 Third International Conference on Artificial Intelligence for Industries (AI4I), pp. 69-74, doi:10.1109/AI4I49448.2020.00023 |
| Nature | **Synthetic**, modeled after a milling machine. It is not real factory telemetry. |
| Size | 10,000 rows, 14 columns, no missing values, no duplicate rows |
| File used | `data/raw/ai4i2020.csv` (file SHA-256 `59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183`; content SHA-256 `6b951bfedd1c42a767117b2bc326e4e3fceac080c7c8a9d87655a46d3dc45a63`, normalised for BOM / line endings) |

**Provenance note:** the copy used for Week 1 was downloaded from a GitHub mirror because UCI was not reachable from the build environment. Its row count, column set and HDF/PWF/OSF counts match the UCI documentation. Re-download from UCI (`python -m pm_ml.download_data`) and confirm the content hash; `tests/test_pipeline.py` fails if the data differs from the one the stored split was made on.

## Columns
| Column | Role | Type / unit | Observed range | Available at prediction time |
|---|---|---|---|---|
| UDI | identifier | int | 1-10000 | no |
| Product ID | identifier (variant serial; **not a machine ID**) | string | 10,000 unique | no |
| Type | feature -> `product_type` | L / M / H | L 6000, M 2997, H 1003 | yes |
| Air temperature [K] | feature | float, K | 295.3 - 304.5 | yes |
| Process temperature [K] | feature | float, K | 305.7 - 313.8 | yes |
| Rotational speed [rpm] | feature | int, rpm | 1168 - 2886 | yes |
| Torque [Nm] | feature | float, Nm | 3.8 - 76.6 | yes |
| Tool wear [min] | feature | int, min | 0 - 253 | yes |
| Machine failure | target (any failure) | 0/1 | 339 ones (3.39%) | no |
| TWF, HDF, PWF, OSF, RNF | targets (failure modes) | 0/1 | 46 / 115 / 95 / 98 / 19 | no |

There is **no timestamp and no machine identifier**. The platform's replay/simulator assigns both.

## Label definitions (from the dataset documentation)
- **TWF** tool wear failure: tool replaced or fails at a randomly chosen wear time between 200 and 240 min.
- **HDF** heat dissipation failure: (process - air temperature) < 8.6 K **and** speed < 1380 rpm.
- **PWF** power failure: power (torque x speed in rad/s) < 3500 W or > 9000 W.
- **OSF** overstrain failure: tool wear x torque > 11,000 / 12,000 / 13,000 minNm for L / M / H.
- **RNF** random failure: 0.1% chance per process, independent of parameters.
- **Machine failure** = 1 if any mode is true.

## Verified facts and known issues (observed in the file)
1. HDF, PWF and OSF rules reproduce their labels **exactly** (115 / 95 / 98 rows, zero disagreements). A model given the derived features can learn the rules; benchmark scores are not evidence of real-world performance.
2. TWF is not a function of the inputs: only about 5-6% of rows with tool wear >= 200 min are TWF.
3. 9 rows have Machine failure = 1 but no mode flagged.
4. 18 of the 19 RNF = 1 rows have Machine failure = 0.
5. 24 failures have 2 or more modes flagged.
6. The documentation text mentions 120 tool-wear events and 5 random failures; the label columns hold 46 TWF and 19 RNF rows. Labels are used as given.
7. Class balance is extreme: 3.39% failures; after the fault-class mapping the smallest classes are TWF (46) and `other` (33).

## Decisions taken for this project
- **Features:** `product_type` + 5 numeric inputs (+ derived `temp_diff_k`, `power_w`, `strain_minnm`, computed only from those inputs). Identifiers and labels are never features.
- **Fault-class target:** `none`, `TWF`, `HDF`, `PWF`, `OSF`, `other` (failure with no flagged mode, or 2+ modes). RNF-only rows stay `none`. No rows removed.
- **Valid API ranges** (wider than observed): air 250-400 K, process 250-450 K, speed 1-10,000 rpm, torque 0-500 Nm, wear 0-1000 min.
- **Split:** stratified on `fault_class`, 60/20/20, seed 42, fixed UDI lists in `data/processed/split.json`.

## Intended and non-intended use
- Intended: building and demonstrating a predictive-maintenance pipeline (ingestion, models, API, dashboard).
- Not intended: claims about real equipment, failure-probability guarantees, remaining useful life, or mixing with other datasets (CWRU, C-MAPSS).

## Privacy
No personal data.
