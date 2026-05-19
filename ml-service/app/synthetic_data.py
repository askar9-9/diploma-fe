from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from app.constants import FEATURE_COLUMNS, TARGET_COLUMN


def _build_row(hour: int, weekday: int, rng: np.random.Generator) -> tuple[dict, str]:
    if 0 <= hour <= 6:
        row = {
            "hour_of_day": hour,
            "weekday": weekday,
            "motion_hall": 0,
            "motion_living": 0,
            "temperature": float(rng.uniform(17.0, 19.0)),
            "light_level": 0.0,
            "tv_on": 0,
            "minutes_idle": int(rng.integers(30, 481)),
        }
        return row, "away"

    if 7 <= hour <= 17:
        row = {
            "hour_of_day": hour,
            "weekday": weekday,
            "motion_hall": 1,
            "motion_living": 1,
            "temperature": float(rng.uniform(21.0, 23.0)),
            "light_level": float(rng.uniform(80.0, 100.0)),
            "tv_on": 0,
            "minutes_idle": int(rng.integers(0, 31)),
        }
        return row, "day"

    if 18 <= hour <= 22:
        if rng.random() < 0.6:
            row = {
                "hour_of_day": hour,
                "weekday": weekday,
                "motion_hall": 0,
                "motion_living": 1,
                "temperature": float(rng.uniform(21.0, 23.0)),
                "light_level": 20.0,
                "tv_on": 1,
                "minutes_idle": int(rng.integers(0, 31)),
            }
            return row, "movie"

        row = {
            "hour_of_day": hour,
            "weekday": weekday,
            "motion_hall": 1,
            "motion_living": 1,
            "temperature": float(rng.uniform(21.0, 23.0)),
            "light_level": float(rng.uniform(80.0, 100.0)),
            "tv_on": 0,
            "minutes_idle": int(rng.integers(0, 31)),
        }
        return row, "day"

    row = {
        "hour_of_day": hour,
        "weekday": weekday,
        "motion_hall": 0,
        "motion_living": 0,
        "temperature": 20.0,
        "light_level": 10.0,
        "tv_on": 0,
        "minutes_idle": int(rng.integers(30, 481)),
    }
    return row, "night"


def generate_synthetic_dataframe(
    rows: int = 2000,
    random_state: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    records: list[dict] = []

    for _ in range(rows):
        hour = int(rng.integers(0, 24))
        weekday = int(rng.integers(0, 7))
        row, scenario = _build_row(hour, weekday, rng)
        records.append({**row, TARGET_COLUMN: scenario})

    return pd.DataFrame(records, columns=[*FEATURE_COLUMNS, TARGET_COLUMN])


def write_synthetic_dataset(output_path: str | Path, rows: int = 2000) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe = generate_synthetic_dataframe(rows=rows, random_state=42)
    dataframe.to_csv(path, index=False)
    return path
