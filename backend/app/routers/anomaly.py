from fastapi import APIRouter, Depends, Request

from pydantic import BaseModel

from app.auth import get_current_user
from app.config import ML_SERVICE_URL
from app.ml_client import MLClient


router = APIRouter(
    prefix="/anomaly",
    tags=["anomaly"],
    dependencies=[Depends(get_current_user)],
)


class AnomalyRequest(BaseModel):
    hour_of_day: int
    weekday: int
    motion_hall: int
    motion_living: int
    temperature: float
    light_level: float
    tv_on: int
    minutes_idle: int


def get_ml_client() -> MLClient:
    return MLClient(ML_SERVICE_URL)


@router.post("/detect")
async def detect_anomaly(
    payload: AnomalyRequest,
    ml: MLClient = Depends(get_ml_client),
) -> dict[str, object]:
    return await ml.anomaly_detect(payload.model_dump())
