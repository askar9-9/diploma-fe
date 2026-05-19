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
