import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth import get_current_user


router = APIRouter(
    prefix="/hems",
    tags=["hems"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/forecast")
async def get_hems_forecast(request: Request) -> dict:
    try:
        return await request.app.state.ml_client.hems_forecast()
    except (httpx.RequestError, httpx.HTTPStatusError) as exc:
        raise HTTPException(status_code=503, detail="ML service unavailable") from exc


@router.get("/status")
async def get_hems_status(request: Request) -> dict:
    try:
        return await request.app.state.ml_client.hems_status()
    except (httpx.RequestError, httpx.HTTPStatusError) as exc:
        raise HTTPException(status_code=503, detail="ML service unavailable") from exc
