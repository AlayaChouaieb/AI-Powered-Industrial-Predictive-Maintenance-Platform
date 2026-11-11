"""Derived features. Pure functions of the prediction-time inputs only."""
import numpy as np
import pandas as pd
from . import config as C


def add_engineered(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    X["temp_diff_k"] = X["process_temperature_k"] - X["air_temperature_k"]
    X["power_w"] = X["torque_nm"] * X["rotational_speed_rpm"] * 2 * np.pi / 60.0
    X["strain_minnm"] = X["tool_wear_min"] * X["torque_nm"]
    return X
