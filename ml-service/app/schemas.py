from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FeatureVector(BaseModel):
    hour_of_day: int
    weekday: int
    motion_hall: int
    motion_living: int
    temperature: float
    light_level: float
    tv_on: int
    minutes_idle: int


class ClassificationResult(BaseModel):
    scenario: str
    confidence: float
    probabilities: dict[str, float]
    alternative: Optional[str]


class ClusterResult(BaseModel):
    n_clusters: int
    labels: list[int]
    centroids: list[list[float]]
    inertia: float


class PatternSuggestion(BaseModel):
    cluster_id: int
    occurrence_count: int
    time_window: dict
    weekdays: list[int]
    median_values: dict


class ClusterRequest(BaseModel):
    vectors: list[FeatureVector]
    n_clusters: int = Field(default=4, ge=1)


class SuggestRequest(BaseModel):
    vectors: list[FeatureVector]
    labels: list[int]
    known_scenarios: list[str]


class TrainRequest(BaseModel):
    vectors: list[FeatureVector]
    labels: list[str]


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool


class ModelInfoResponse(BaseModel):
    version: str
    trained_at: str | None
    n_classes: int
    accuracy: float


class EnergyHourForecast(BaseModel):
    hour: int
    offset_hours: int
    scenario: str
    confidence: float
    consumption_wh: float
    consumption_kwh: float
    devices: dict[str, float]


class EnergyForecastResponse(BaseModel):
    current_hour: int
    weekday: int
    forecast: list[EnergyHourForecast]
    total_kwh: float
    peak_hour: int
    peak_consumption_wh: float
    recommendations: list[str]


class EnergyForecastRequest(BaseModel):
    current_hour: int = Field(ge=0, le=23)
    weekday: int = Field(ge=0, le=6)


class AnomalyRequest(BaseModel):
    hour_of_day: int
    weekday: int
    motion_hall: int
    motion_living: int
    temperature: float
    light_level: float
    tv_on: int
    minutes_idle: int


class AnomalyResult(BaseModel):
    anomaly: bool
    score: float
    reason: str
