from __future__ import annotations

import os
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "data" / "models" / "classifier.joblib"
CLASSES = ["day", "night", "away", "movie"]
FEATURES = [
    "hour_of_day",
    "weekday",
    "motion_hall",
    "motion_living",
    "temperature",
    "light_level",
    "tv_on",
    "minutes_idle",
]


def generate_synthetic_data(n_samples: int = 2400) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    per_class = max(n_samples // len(CLASSES), 500)
    samples: list[list[float]] = []
    labels: list[str] = []

    def bounded_uniform(low: float, high: float, sigma: float) -> float:
        value = rng.uniform(low, high) + rng.normal(0.0, sigma)
        return float(np.clip(value, low, high))

    def add_sample(label: str, values: list[float]) -> None:
        samples.append(values)
        labels.append(label)

    # Synthetic samples reflect the known scene rules with added noise so the model
    # tolerates slightly imperfect sensor readings.
    for _ in range(per_class):
        add_sample(
            "day",
            [
                bounded_uniform(7, 19, 0.45),
                float(rng.integers(0, 7)),
                float(rng.integers(0, 2)),
                float(rng.integers(0, 2)),
                bounded_uniform(20, 25, 0.7),
                bounded_uniform(60, 100, 5.0),
                0.0,
                bounded_uniform(0, 30, 5.0),
            ],
        )

    for _ in range(per_class):
        night_hour = (
            bounded_uniform(22, 23.99, 0.3)
            if rng.random() > 0.5
            else bounded_uniform(0, 6.99, 0.3)
        )
        add_sample(
            "night",
            [
                night_hour,
                float(rng.integers(0, 7)),
                float(rng.binomial(1, 0.15)),
                float(rng.binomial(1, 0.1)),
                bounded_uniform(18, 22, 0.6),
                bounded_uniform(0, 20, 3.0),
                0.0,
                bounded_uniform(30, 480, 20.0),
            ],
        )

    for _ in range(per_class):
        add_sample(
            "away",
            [
                bounded_uniform(0, 23.99, 0.4),
                float(rng.integers(0, 7)),
                0.0,
                0.0,
                bounded_uniform(16, 20, 0.6),
                bounded_uniform(0, 30, 4.0),
                0.0,
                bounded_uniform(90, 480, 30.0),
            ],
        )

    for _ in range(per_class):
        add_sample(
            "movie",
            [
                bounded_uniform(18, 23.99, 0.35),
                float(rng.integers(0, 7)),
                float(rng.binomial(1, 0.35)),
                1.0,
                bounded_uniform(20, 24, 0.6),
                bounded_uniform(10, 30, 3.0),
                1.0,
                bounded_uniform(0, 30, 5.0),
            ],
        )

    X = np.asarray(samples, dtype=np.float32)
    y = np.asarray(labels, dtype=object)
    order = rng.permutation(len(y))
    return X[order], y[order]


class SceneClassifier:
    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = Path(model_path) if model_path else MODEL_PATH
        self.model: RandomForestClassifier | None = None
        self._load_or_train()

    def _load_or_train(self) -> None:
        os.makedirs(self.model_path.parent, exist_ok=True)

        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                return
            except Exception:
                self.model = None

        X_train, y_train = generate_synthetic_data()
        self.model = RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=2,
            random_state=42,
            class_weight="balanced_subsample",
        )
        self.model.fit(X_train, y_train)
        joblib.dump(self.model, self.model_path)

    @staticmethod
    def _binary(value: float) -> float:
        return 1.0 if float(value) >= 0.5 else 0.0

    def _vectorize(self, features: dict[str, float]) -> np.ndarray:
        sanitized = {
            "hour_of_day": float(np.clip(float(features["hour_of_day"]), 0.0, 23.0)),
            "weekday": float(np.clip(float(features["weekday"]), 0.0, 6.0)),
            "motion_hall": self._binary(features["motion_hall"]),
            "motion_living": self._binary(features["motion_living"]),
            "temperature": float(features["temperature"]),
            "light_level": float(max(0.0, float(features["light_level"]))),
            "tv_on": self._binary(features["tv_on"]),
            "minutes_idle": float(max(0.0, float(features["minutes_idle"]))),
        }
        return np.asarray([[sanitized[name] for name in FEATURES]], dtype=np.float32)

    def predict(self, features: dict[str, float]) -> dict[str, object]:
        if self.model is None:
            raise RuntimeError("Scene classifier is not initialized")

        vector = self._vectorize(features)
        probabilities = self.model.predict_proba(vector)[0]
        raw_scores = {label: 0.0 for label in CLASSES}
        for label, score in zip(self.model.classes_, probabilities):
            raw_scores[str(label)] = float(score)

        ranked = sorted(raw_scores.items(), key=lambda item: item[1], reverse=True)
        scenario, confidence = ranked[0]
        alternative = ranked[1][0] if len(ranked) > 1 else scenario

        return {
            "scenario": scenario,
            "confidence": round(confidence, 4),
            "probabilities": {
                label: round(raw_scores[label], 4)
                for label in CLASSES
            },
            "alternative": alternative,
        }
