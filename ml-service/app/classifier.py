from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app.constants import FEATURE_COLUMNS, TARGET_CLASSES, TARGET_COLUMN
from app.schemas import ClassificationResult, FeatureVector
from app.synthetic_data import generate_synthetic_dataframe


class ScenarioClassifier:
    def __init__(self):
        self.model = None
        self.classes_ = []
        self.accuracy_ = 0.0
        self.trained_at = None
        self.version_ = None

    def train(self, X: np.ndarray, y: list[str]) -> dict:
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)

        present_classes = set(y)
        self.classes_ = [label for label in TARGET_CLASSES if label in present_classes]
        self.accuracy_ = float(self.model.score(X, y))
        self.trained_at = datetime.now(UTC).isoformat()

        return {"accuracy": self.accuracy_, "classes": self.classes_}

    def predict(self, fv: dict) -> ClassificationResult:
        if self.model is None:
            raise ValueError("Classifier is not trained")

        missing_features = [column for column in FEATURE_COLUMNS if column not in fv]
        if missing_features:
            raise ValueError(f"Missing features: {', '.join(missing_features)}")

        feature_vector = FeatureVector(**fv)
        feature_array = np.array(
            [[getattr(feature_vector, column) for column in FEATURE_COLUMNS]],
            dtype=float,
        )

        probabilities = self.model.predict_proba(feature_array)[0]
        probability_map = {
            class_name: float(probability)
            for class_name, probability in zip(self.model.classes_, probabilities)
        }
        ordered = sorted(probability_map.items(), key=lambda item: item[1], reverse=True)
        scenario, confidence = ordered[0]
        alternative = ordered[1][0] if len(ordered) > 1 else None

        return ClassificationResult(
            scenario=scenario,
            confidence=float(confidence),
            probabilities=probability_map,
            alternative=alternative if alternative != scenario else None,
        )

    def save(self, path: str):
        if self.model is None:
            raise ValueError("Classifier is not trained")

        payload = {
            "model": self.model,
            "classes": self.classes_,
            "accuracy": self.accuracy_,
            "trained_at": self.trained_at,
            "version": self.version_,
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(payload, path)

    def load(self, path: str):
        payload = joblib.load(path)
        self.model = payload["model"]
        self.classes_ = list(payload.get("classes", getattr(self.model, "classes_", [])))
        self.accuracy_ = float(payload.get("accuracy", 0.0))
        self.trained_at = payload.get("trained_at")
        self.version_ = payload.get("version") or Path(path).stem.removeprefix("classifier_")

    def _make_synthetic_data(self) -> tuple[np.ndarray, list[str]]:
        dataframe = generate_synthetic_dataframe(rows=2000, random_state=42)
        X = dataframe[FEATURE_COLUMNS].to_numpy(dtype=float)
        y = dataframe[TARGET_COLUMN].tolist()
        return X, y
