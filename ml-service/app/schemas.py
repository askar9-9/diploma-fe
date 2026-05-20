from typing import Literal

from pydantic import BaseModel, Field


class OptimizeRequest(BaseModel):
    load_forecast: list[float] = Field(..., min_length=24, max_length=24)
    solar_forecast: list[float] = Field(..., min_length=24, max_length=24)
    battery_capacity: float = Field(..., ge=0)
    initial_soc: float = Field(..., ge=0)
    max_charge_rate: float = Field(..., ge=0)
    max_discharge_rate: float = Field(..., ge=0)
    prices: list[float] = Field(..., min_length=24, max_length=24)


class ScheduleStep(BaseModel):
    hour: int
    charge: float
    discharge: float
    grid_import: float
    battery_soc: float


class OptimizeResponse(BaseModel):
    schedule: list[ScheduleStep]
    total_cost: float


SceneLabel = Literal["day", "night", "away", "movie"]


class SceneFeatures(BaseModel):
    hour_of_day: float
    weekday: float
    motion_hall: float
    motion_living: float
    temperature: float
    light_level: float
    tv_on: float
    minutes_idle: float


class ClassifyRequest(BaseModel):
    features: SceneFeatures


class ClassifyResponse(BaseModel):
    scenario: SceneLabel
    confidence: float
    probabilities: dict[str, float]
    alternative: SceneLabel
