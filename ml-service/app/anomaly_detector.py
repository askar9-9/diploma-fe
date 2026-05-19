from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest

from app.constants import FEATURE_COLUMNS


class AnomalyDetector:
    def __init__(self):
        self.model: IsolationForest | None = None

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self, X: np.ndarray) -> dict:
        self.model = IsolationForest(
            contamination=0.05,
            random_state=42,
            n_estimators=100,
        )
        self.model.fit(X)
        return {"trained": True, "n_samples": len(X)}

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def detect(self, fv: dict) -> dict:
        if self.model is None:
            raise ValueError("AnomalyDetector is not trained")

        feature_array = np.array(
            [[fv[col] for col in FEATURE_COLUMNS]],
            dtype=float,
        )

        # decision_function: higher values = more normal
        score = float(self.model.decision_function(feature_array)[0])
        prediction = self.model.predict(feature_array)[0]  # -1 = anomaly, 1 = normal
        is_anomaly = bool(prediction == -1)

        reason = self._explain(fv, is_anomaly)
        return {"anomaly": is_anomaly, "score": score, "reason": reason}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _explain(self, fv: dict, is_anomaly: bool) -> str:
        minutes_idle = fv.get("minutes_idle", 0)
        temperature = fv.get("temperature", 20.0)
        hour = fv.get("hour_of_day", 12)
        light_level = fv.get("light_level", 0.0)
        motion_hall = fv.get("motion_hall", 0)
        motion_living = fv.get("motion_living", 0)

        if minutes_idle > 120 and temperature > 24:
            return "High temperature with no motion"

        if (
            0 <= hour <= 5
            and light_level > 50
            and motion_hall == 0
            and motion_living == 0
        ):
            return "Lights on at night with no motion"

        if temperature < 16:
            return "Unusually low temperature"

        if is_anomaly:
            return "Unusual pattern detected"

        return "Normal behavior"

    def _make_normal_data(self, n: int, random_state: int = 42) -> np.ndarray:
        """Generate n rows of synthetic normal behavior in FEATURE_COLUMNS order."""
        rng = np.random.default_rng(random_state)
        rows: list[list[float]] = []

        for _ in range(n):
            hour = int(rng.integers(0, 24))
            weekday = int(rng.integers(0, 7))

            if 0 <= hour <= 6:
                # away / sleeping
                row = [
                    hour,
                    weekday,
                    0,  # motion_hall
                    0,  # motion_living
                    float(rng.normal(18.0, 0.5)),   # temperature
                    float(max(0.0, rng.normal(0.0, 2.0))),  # light_level
                    0,  # tv_on
                    int(np.clip(rng.normal(200, 60), 30, 480)),  # minutes_idle
                ]
            elif 7 <= hour <= 17:
                # day activity
                row = [
                    hour,
                    weekday,
                    int(rng.integers(0, 2)),  # motion_hall
                    int(rng.integers(0, 2)),  # motion_living
                    float(rng.normal(22.0, 0.5)),   # temperature
                    float(np.clip(rng.normal(90.0, 5.0), 70.0, 100.0)),  # light_level
                    0,  # tv_on
                    int(np.clip(rng.normal(10, 8), 0, 60)),  # minutes_idle
                ]
            elif 18 <= hour <= 22:
                # evening: movie or day
                if rng.random() < 0.6:
                    row = [
                        hour,
                        weekday,
                        0,  # motion_hall
                        1,  # motion_living
                        float(rng.normal(22.0, 0.5)),   # temperature
                        20.0,   # light_level
                        1,  # tv_on
                        int(np.clip(rng.normal(10, 8), 0, 60)),  # minutes_idle
                    ]
                else:
                    row = [
                        hour,
                        weekday,
                        1,  # motion_hall
                        1,  # motion_living
                        float(rng.normal(22.0, 0.5)),   # temperature
                        float(np.clip(rng.normal(90.0, 5.0), 70.0, 100.0)),  # light_level
                        0,  # tv_on
                        int(np.clip(rng.normal(10, 8), 0, 60)),  # minutes_idle
                    ]
            else:
                # night (23)
                row = [
                    hour,
                    weekday,
                    0,  # motion_hall
                    0,  # motion_living
                    float(rng.normal(20.0, 0.3)),   # temperature
                    float(max(0.0, rng.normal(10.0, 2.0))),  # light_level
                    0,  # tv_on
                    int(np.clip(rng.normal(150, 60), 30, 480)),  # minutes_idle
                ]

            rows.append(row)

        return np.array(rows, dtype=float)
