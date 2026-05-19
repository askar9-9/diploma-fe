from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
from fastapi import FastAPI

from app.anomaly_detector import AnomalyDetector
from app.classifier import ScenarioClassifier
from app.clusterer import ScenarioClusterer
from app.constants import FEATURE_COLUMNS
from app.energy_forecaster import EnergyForecaster
from app.model_store import MODEL_PATH, load_latest_model, save_model
from app.schemas import (
    AnomalyRequest,
    AnomalyResult,
    ClassificationResult,
    ClusterRequest,
    ClusterResult,
    EnergyForecastRequest,
    EnergyForecastResponse,
    FeatureVector,
    PatternSuggestion,
    SuggestRequest,
    TrainRequest,
)
from app.suggester import PatternSuggester
from app.synthetic_data import write_synthetic_dataset

classifier = ScenarioClassifier()
clusterer = ScenarioClusterer()
suggester = PatternSuggester()
energy_forecaster = EnergyForecaster()
anomaly_detector = AnomalyDetector()


def _bootstrap_classifier() -> None:
    if load_latest_model(classifier):
        return

    dataset_path = Path("data/synthetic_train.csv")
    write_synthetic_dataset(dataset_path, rows=2000)

    X, y = classifier._make_synthetic_data()
    classifier.train(X, y)
    save_model(classifier)


def _bootstrap_anomaly_detector() -> None:
    X_normal = anomaly_detector._make_normal_data(1000)
    anomaly_detector.train(X_normal)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path(MODEL_PATH).mkdir(parents=True, exist_ok=True)
    _bootstrap_classifier()
    _bootstrap_anomaly_detector()
    yield


app = FastAPI(title="HomeIQ ML Service", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": classifier.model is not None}


@app.post("/classify", response_model=ClassificationResult)
def classify(feature_vector: FeatureVector) -> ClassificationResult:
    return classifier.predict(feature_vector.model_dump())


@app.post("/energy/forecast", response_model=EnergyForecastResponse)
def forecast_energy(request: EnergyForecastRequest) -> EnergyForecastResponse:
    """Прогноз энергопотребления на 24 часа."""
    forecast = energy_forecaster.forecast_24h(
        classifier,
        request.current_hour,
        request.weekday,
    )
    peak = energy_forecaster.peak_hour(forecast)
    return EnergyForecastResponse(
        current_hour=request.current_hour,
        weekday=request.weekday,
        forecast=forecast,
        total_kwh=energy_forecaster.daily_total_kwh(forecast),
        peak_hour=peak["hour"],
        peak_consumption_wh=peak["consumption_wh"],
        recommendations=energy_forecaster.recommendations(forecast),
    )


@app.post("/cluster", response_model=ClusterResult)
def cluster(request: ClusterRequest) -> ClusterResult:
    return clusterer.fit_predict(
        [vector.model_dump() for vector in request.vectors],
        n_clusters=request.n_clusters,
    )


@app.post("/suggest", response_model=list[PatternSuggestion])
def suggest(request: SuggestRequest) -> list[PatternSuggestion]:
    return suggester.suggest(
        vectors=[vector.model_dump() for vector in request.vectors],
        labels=request.labels,
        known_scenarios=request.known_scenarios,
    )


@app.post("/train")
def train(request: TrainRequest) -> dict:
    X = np.array(
        [
            [getattr(vector, column) for column in FEATURE_COLUMNS]
            for vector in request.vectors
        ],
        dtype=float,
    )
    result = classifier.train(X, request.labels)
    version_path = save_model(classifier)
    version = Path(version_path).stem.removeprefix("classifier_")
    return {"accuracy": result["accuracy"], "version": version}


@app.get("/model/info")
def model_info() -> dict:
    return {
        "version": classifier.version_ or "",
        "trained_at": classifier.trained_at,
        "n_classes": len(classifier.classes_),
        "accuracy": classifier.accuracy_,
    }


@app.post("/anomaly/detect", response_model=AnomalyResult)
def detect_anomaly(request: AnomalyRequest) -> AnomalyResult:
    result = anomaly_detector.detect(request.model_dump())
    return AnomalyResult(**result)
