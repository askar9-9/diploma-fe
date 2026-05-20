from __future__ import annotations

import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import MinMaxScaler

try:
    import tensorflow as tf
except ImportError as exc:
    raise RuntimeError(
        "TensorFlow is required to train the LSTM model. "
        "Install dependencies from ml-service/requirements.txt first."
    ) from exc


INPUT_WINDOW = 168
FORECAST_HORIZON = 24
FEATURE_COLUMNS = [
    "consumption_kwh",
    "hour_sin",
    "hour_cos",
    "weekday_sin",
    "weekday_cos",
]


def build_features(frame: pd.DataFrame, scaler: MinMaxScaler) -> pd.DataFrame:
    features = pd.DataFrame(index=frame.index)

    scaled_consumption = scaler.transform(frame[["consumption_kwh"]]).reshape(-1)
    hours = frame.index.hour.to_numpy()
    weekdays = frame.index.dayofweek.to_numpy()

    features["consumption_kwh"] = scaled_consumption
    features["hour_sin"] = np.sin(2 * np.pi * hours / 24)
    features["hour_cos"] = np.cos(2 * np.pi * hours / 24)
    features["weekday_sin"] = np.sin(2 * np.pi * weekdays / 7)
    features["weekday_cos"] = np.cos(2 * np.pi * weekdays / 7)

    return features


def create_sequences(features: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    values = features[FEATURE_COLUMNS].to_numpy(dtype=np.float32)
    target = features["consumption_kwh"].to_numpy(dtype=np.float32)

    X, y = [], []
    max_start = len(values) - INPUT_WINDOW - FORECAST_HORIZON + 1
    for start in range(max_start):
        end = start + INPUT_WINDOW
        target_end = end + FORECAST_HORIZON
        X.append(values[start:end])
        y.append(target[end:target_end])

    if not X:
        raise ValueError("Not enough hourly observations to create LSTM sequences.")

    return np.asarray(X, dtype=np.float32), np.asarray(y, dtype=np.float32)


def build_model() -> tf.keras.Model:
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(INPUT_WINDOW, len(FEATURE_COLUMNS))),
            tf.keras.layers.LSTM(64, return_sequences=True),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(32),
            tf.keras.layers.Dense(FORECAST_HORIZON),
        ]
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss="mae",
        metrics=["mae"],
    )
    return model


def inverse_transform_batch(
    scaler: MinMaxScaler,
    values: np.ndarray,
) -> np.ndarray:
    return scaler.inverse_transform(values.reshape(-1, 1)).reshape(values.shape)


def main() -> None:
    tf.random.set_seed(42)
    np.random.seed(42)

    project_root = Path(__file__).resolve().parents[1]
    dataset_path = project_root / "data" / "uci_hourly.parquet"
    models_dir = project_root / "data" / "models"
    model_path = models_dir / "lstm_consumption.keras"
    scaler_path = models_dir / "scaler.pkl"

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {dataset_path}. Run scripts/prepare_uci.py first."
        )

    try:
        frame = pd.read_parquet(dataset_path)
    except ImportError as exc:
        raise RuntimeError(
            "Parquet support is unavailable. Install a parquet engine such as "
            "'pyarrow' before training."
        ) from exc

    if "consumption_kwh" not in frame.columns:
        raise ValueError("Expected 'consumption_kwh' column in prepared dataset.")

    frame = frame.sort_index().dropna()
    train_cutoff = max(INPUT_WINDOW + FORECAST_HORIZON, int(len(frame) * 0.8))
    scaler = MinMaxScaler()
    scaler.fit(frame.iloc[:train_cutoff][["consumption_kwh"]])
    features = build_features(frame, scaler)
    X, y = create_sequences(features)

    split_index = max(1, min(int(len(X) * 0.8), len(X) - 1))
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]

    if len(X_test) == 0:
        raise ValueError("Test split is empty. Add more training data.")

    model = build_model()
    model.fit(
        X_train,
        y_train,
        epochs=30,
        batch_size=32,
        validation_split=0.1,
        shuffle=False,
        verbose=1,
    )

    predictions_scaled = model.predict(X_test, verbose=0)
    y_test_unscaled = inverse_transform_batch(scaler, y_test)
    predictions_unscaled = inverse_transform_batch(scaler, predictions_scaled)

    mae = mean_absolute_error(
        y_test_unscaled.reshape(-1),
        predictions_unscaled.reshape(-1),
    )
    denominator = np.clip(np.abs(y_test_unscaled.reshape(-1)), 1e-6, None)
    mape = np.mean(
        np.abs(
            (y_test_unscaled.reshape(-1) - predictions_unscaled.reshape(-1))
            / denominator
        )
    ) * 100

    os.makedirs(models_dir, exist_ok=True)
    model.save(model_path)
    joblib.dump(scaler, scaler_path)

    print(f"Saved model to {model_path}")
    print(f"Saved scaler to {scaler_path}")
    print(f"Test MAE: {mae:.3f}")
    print(f"Test MAPE: {mape:.3f}%")


if __name__ == "__main__":
    main()
