from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import DEVICE_SIMULATOR_URL
from app.db import get_db
from app.ml_features import normalize_device_item
from db.models import DeviceState


router = APIRouter(
    prefix="/devices",
    tags=["devices"],
    dependencies=[Depends(get_current_user)],
)


class DeviceCommandRequest(BaseModel):
    value: float


def _device_detail_from_response(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict) and payload.get("detail"):
        return str(payload["detail"])
    if response.text:
        return response.text
    return "Device simulator error"


async def _proxy_request(
    method: str,
    path: str,
    payload: Optional[dict[str, Any]] = None,
) -> httpx.Response:
    try:
        async with httpx.AsyncClient(
            base_url=DEVICE_SIMULATOR_URL.rstrip("/"),
            timeout=5.0,
        ) as client:
            return await client.request(method, path, json=payload)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail="Device simulator unavailable") from exc


@router.get("")
async def list_devices(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    response = await _proxy_request("GET", "/devices")
    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=_device_detail_from_response(response),
        )

    payload = response.json()
    states = {state.id: state for state in db.query(DeviceState).all()}

    if isinstance(payload, list):
        items: List[Dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            device_id = str(item.get("id") or item.get("device_id") or "")
            if not device_id:
                continue
            items.append(normalize_device_item(device_id, item, states.get(device_id)))
        return items

    if isinstance(payload, dict):
        items = [
            normalize_device_item(device_id, data, states.get(device_id))
            for device_id, data in payload.items()
            if isinstance(data, dict)
        ]
        return sorted(items, key=lambda item: str(item["id"]))

    return []


@router.post("/{device_id}/command")
async def send_device_command(
    device_id: str,
    payload: DeviceCommandRequest,
) -> dict[str, Any]:
    response = await _proxy_request(
        "POST",
        f"/devices/{device_id}/command",
        {"value": payload.value},
    )
    if response.status_code in {404, 405}:
        response = await _proxy_request(
            "POST",
            f"/devices/{device_id}/state",
            {"value": payload.value},
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=_device_detail_from_response(response),
        )

    return response.json()
