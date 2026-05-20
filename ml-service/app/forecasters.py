from __future__ import annotations

import math
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path

try:
    import joblib
except ModuleNotFoundError:
    import pickle

    class _JoblibCompat:
        @staticmethod
        def dump(obj: object, filename: str | Path) -> None:
            with Path(filename).open("wb") as handle:
                pickle.dump(obj, handle)

        @staticmethod
        def load(filename: str | Path) -> object:
            with Path(filename).open("rb") as handle:
                return pickle.load(handle)

    joblib = _JoblibCompat()

try:
    import numpy as np
except ModuleNotFoundError:
    np = None


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "data" / "models" / "lstm_consumption.keras"
SCALER_PATH = BASE_DIR / "data" / "models" / "scaler.pkl"
INPUT_WINDOW = 168
FORECAST_HORIZON = 24


def _baseline_consumption_for_hour(hour: int) -> float:
    if 18 <= hour < 22:
        return 2.5
    if 7 <= hour < 18:
        return 1.5
    return 1.0


def build_fallback_curve(start_hour: int, horizon: int = FORECAST_HORIZON) -> list[float]:
    return [
        round(float(_baseline_consumption_for_hour((start_hour + step) % 24)), 3)
        for step in range(horizon)
    ]


def build_fallback_history(
    current_hour: int,
    length: int = INPUT_WINDOW,
) -> list[float]:
    history = []
    for offset in range(length, 0, -1):
        hour = (current_hour - offset) % 24
        history.append(float(_baseline_consumption_for_hour(hour)))
    return history


class LightGBMForecaster:
    """LightGBM load forecaster. Trains on synthetic data at startup if no saved model."""

    _MODEL_PATH = BASE_DIR / "data" / "models" / "lgbm_load.pkl"

    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = Path(model_path) if model_path else self._MODEL_PATH
        self.model = None
        self._train_or_load()

    def _baseline(self, hour: int) -> float:
        if 18 <= hour < 22:
            return 2.5
        if 7 <= hour < 18:
            return 1.5
        return 1.0

    def _generate_synthetic(self):
        import pandas as pd
        import random

        rng = random.Random(42)
        rows = []
        for day in range(28):
            weekday = day % 7
            for hour in range(24):
                base = self._baseline(hour) * (1.2 if weekday >= 5 else 1.0)
                consumption = max(0.1, base + rng.gauss(0, 0.15))
                rows.append(
                    {
                        "hour": hour,
                        "weekday": weekday,
                        "hour_sin": math.sin(2 * math.pi * hour / 24),
                        "hour_cos": math.cos(2 * math.pi * hour / 24),
                        "weekday_sin": math.sin(2 * math.pi * weekday / 7),
                        "weekday_cos": math.cos(2 * math.pi * weekday / 7),
                        "lag_24h": self._baseline((hour - 24) % 24),
                        "lag_168h": self._baseline(hour),
                        "consumption": consumption,
                    }
                )
        return pd.DataFrame(rows)

    def _train_or_load(self) -> None:
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                return
            except Exception:
                pass
        try:
            import lightgbm as lgb

            df = self._generate_synthetic()
            features = [
                "hour",
                "hour_sin",
                "hour_cos",
                "weekday_sin",
                "weekday_cos",
                "lag_24h",
                "lag_168h",
            ]
            self.model = lgb.LGBMRegressor(
                n_estimators=100,
                learning_rate=0.1,
                num_leaves=31,
                random_state=42,
                verbose=-1,
            )
            self.model.fit(df[features].values, df["consumption"].values)
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(self.model, self.model_path)
        except Exception:
            self.model = None

    @property
    def is_ready(self) -> bool:
        return self.model is not None

    def predict_load(self, start_hour: int, weekday: int | None = None) -> list[float]:
        if not self.is_ready:
            return build_fallback_curve(start_hour)
        if weekday is None:
            weekday = datetime.now().weekday()
        try:
            import pandas as pd

            rows = []
            for step in range(FORECAST_HORIZON):
                hour = (start_hour + step) % 24
                rows.append(
                    {
                        "hour": hour,
                        "hour_sin": math.sin(2 * math.pi * hour / 24),
                        "hour_cos": math.cos(2 * math.pi * hour / 24),
                        "weekday_sin": math.sin(2 * math.pi * weekday / 7),
                        "weekday_cos": math.cos(2 * math.pi * weekday / 7),
                        "lag_24h": self._baseline((hour - 24) % 24),
                        "lag_168h": self._baseline(hour),
                    }
                )
            X = pd.DataFrame(rows)[
                [
                    "hour",
                    "hour_sin",
                    "hour_cos",
                    "weekday_sin",
                    "weekday_cos",
                    "lag_24h",
                    "lag_168h",
                ]
            ].values
            preds = self.model.predict(X)
            return [round(float(max(0.1, v)), 3) for v in preds]
        except Exception:
            return build_fallback_curve(start_hour)


@lru_cache(maxsize=1)
def get_lgbm_forecaster() -> LightGBMForecaster:
    return LightGBMForecaster()


class LSTMForecaster:
    def __init__(
        self,
        model_path: Path | None = None,
        scaler_path: Path | None = None,
    ) -> None:
        self.model_path = Path(model_path or MODEL_PATH)
        self.scaler_path = Path(scaler_path or SCALER_PATH)
        self.model = None
        self.scaler = None
        self._load_model()

    def _load_model(self) -> None:
        if not self.model_path.exists() or not self.scaler_path.exists():
            return

        try:
            import tensorflow as tf

            self.model = tf.keras.models.load_model(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
        except Exception:
            self.model = None
            self.scaler = None

    @property
    def is_ready(self) -> bool:
        return self.model is not None and self.scaler is not None

    @staticmethod
    def _coerce_float(value: float) -> float | None:
        try:
            candidate = float(value)
        except (TypeError, ValueError):
            return None
        return candidate if math.isfinite(candidate) else None

    def _prepare_history(self, history_168h: list[float]) -> list[float]:
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        cleaned = []
        for value in history_168h:
            coerced = self._coerce_float(value)
            if coerced is not None:
                cleaned.append(coerced)

        if len(cleaned) >= INPUT_WINDOW:
            return cleaned[-INPUT_WINDOW:]

        fallback = build_fallback_history(now.hour, INPUT_WINDOW)
        if not cleaned:
            return fallback

        missing = INPUT_WINDOW - len(cleaned)
        return fallback[:missing] + cleaned

    def _build_feature_window(self, history_168h: list[float]) -> np.ndarray:
        if np is None:
            raise RuntimeError("numpy is not installed")
        history = np.asarray(self._prepare_history(history_168h), dtype=np.float32)
        reference_time = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
        timestamps = [
            reference_time - timedelta(hours=INPUT_WINDOW - 1 - index)
            for index in range(INPUT_WINDOW)
        ]

        scaled_consumption = self.scaler.transform(history.reshape(-1, 1)).reshape(-1)
        hours = np.asarray([timestamp.hour for timestamp in timestamps], dtype=np.float32)
        weekdays = np.asarray(
            [timestamp.weekday() for timestamp in timestamps],
            dtype=np.float32,
        )

        feature_window = np.column_stack(
            [
                scaled_consumption,
                np.sin(2 * np.pi * hours / 24),
                np.cos(2 * np.pi * hours / 24),
                np.sin(2 * np.pi * weekdays / 7),
                np.cos(2 * np.pi * weekdays / 7),
            ]
        )
        return feature_window.astype(np.float32)

    def predict_load(self, history_168h: list[float]) -> list[float]:
        start_hour = datetime.now().hour
        if not self.is_ready or np is None:
            return build_fallback_curve(start_hour)

        try:
            features = self._build_feature_window(history_168h)
            prediction_scaled = self.model.predict(
                features[np.newaxis, :, :],
                verbose=0,
            )[0]
            prediction = self.scaler.inverse_transform(
                np.asarray(prediction_scaled).reshape(-1, 1)
            ).reshape(-1)

            return [
                round(float(max(0.0, value)), 3)
                for value in prediction[:FORECAST_HORIZON]
            ]
        except Exception:
            return build_fallback_curve(start_hour)


@lru_cache(maxsize=1)
def get_lstm_forecaster() -> LSTMForecaster:
    return LSTMForecaster()


def predict_load(history_168h: list[float]) -> list[float]:
    return get_lstm_forecaster().predict_load(history_168h)


def _seasonal_multiplier(month: int) -> float:
    if month in {12, 1, 2}:
        return 0.6
    if month in {3, 4, 5}:
        return 0.85
    if month in {6, 7, 8}:
        return 1.0
    return 0.75


def predict_solar(hour: int, month: int) -> list[float]:
    multiplier = _seasonal_multiplier(month)
    forecast = []

    for step in range(FORECAST_HORIZON):
        current_hour = (hour + step) % 24
        if 6 <= current_hour <= 20:
            generation = max(
                0.0,
                5.0 * math.sin(math.pi * (current_hour - 6) / 14),
            )
            forecast.append(round(float(generation * multiplier), 3))
        else:
            forecast.append(0.0)

    return forecast
