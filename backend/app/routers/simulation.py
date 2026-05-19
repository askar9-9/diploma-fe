from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
import httpx

from app.auth import get_current_user
from app.config import DEVICE_SIMULATOR_URL


router = APIRouter(
    prefix="/simulation",
    tags=["simulation"],
    dependencies=[Depends(get_current_user)],
)


class SimulationStartRequest(BaseModel):
    speed: int = Field(default=60, ge=1)


@router.post("/start")
async def start_simulation(payload: SimulationStartRequest) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{DEVICE_SIMULATOR_URL}/simulation/start",
            json={"speed": payload.speed},
            timeout=5.0,
        )
        resp.raise_for_status()
        return resp.json()


@router.post("/stop")
async def stop_simulation() -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{DEVICE_SIMULATOR_URL}/simulation/stop",
            timeout=5.0,
        )
        resp.raise_for_status()
        return resp.json()


@router.get("/status")
async def get_simulation_status() -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{DEVICE_SIMULATOR_URL}/simulation/status",
            timeout=5.0,
        )
        resp.raise_for_status()
        return resp.json()
