from __future__ import annotations

import os
from datetime import datetime, UTC
from pathlib import Path

MODEL_PATH = os.getenv("MODEL_PATH", "data/models/")


def _model_dir() -> Path:
    path = Path(MODEL_PATH)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_model(classifier) -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    path = _model_dir() / f"classifier_{timestamp}.joblib"
    classifier.version_ = timestamp
    classifier.save(str(path))
    return str(path)


def load_latest_model(classifier) -> bool:
    model_files = sorted(_model_dir().glob("classifier_*.joblib"))
    if not model_files:
        return False

    latest = model_files[-1]
    classifier.load(str(latest))
    classifier.version_ = latest.stem.removeprefix("classifier_")
    return True
