from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests


UCI_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/00235/"
    "household_power_consumption.zip"
)
ARCHIVE_MEMBER = "household_power_consumption.txt"


def prepare_uci_dataset() -> Path:
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    output_path = data_dir / "uci_hourly.parquet"
    data_dir.mkdir(parents=True, exist_ok=True)

    response = requests.get(UCI_URL, timeout=120)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        with archive.open(ARCHIVE_MEMBER) as dataset_file:
            frame = pd.read_csv(
                dataset_file,
                sep=";",
                usecols=["Date", "Time", "Global_active_power"],
                na_values="?",
                low_memory=False,
            )

    frame["timestamp"] = pd.to_datetime(
        frame["Date"] + " " + frame["Time"],
        format="%d/%m/%Y %H:%M:%S",
    )
    frame["Global_active_power"] = pd.to_numeric(
        frame["Global_active_power"],
        errors="coerce",
    )

    hourly = (
        frame.set_index("timestamp")[["Global_active_power"]]
        .rename(columns={"Global_active_power": "consumption_kwh"})
        .resample("H")
        .mean()
        .dropna()
    )

    try:
        hourly.to_parquet(output_path)
    except ImportError as exc:
        raise RuntimeError(
            "Parquet support is unavailable. Install a parquet engine such as "
            "'pyarrow' before running this script."
        ) from exc

    return output_path


if __name__ == "__main__":
    saved_path = prepare_uci_dataset()
    print(f"Saved hourly UCI dataset to {saved_path}")
