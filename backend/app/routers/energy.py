from datetime import datetime

from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.config import ML_SERVICE_URL
from app.ml_client import MLClient


router = APIRouter(prefix="/energy", tags=["energy"])


def get_ml_client() -> MLClient:
    return MLClient(ML_SERVICE_URL)


@router.get("/forecast")
async def get_energy_forecast(
    current_user=Depends(get_current_user),
    ml: MLClient = Depends(get_ml_client),
):
    """Прогноз энергопотребления на 24 часа."""
    now = datetime.utcnow()
    return await ml.energy_forecast(now.hour, now.weekday())
