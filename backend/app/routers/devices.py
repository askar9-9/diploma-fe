from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from db.models import Device


router = APIRouter(
    prefix="/devices",
    tags=["devices"],
    dependencies=[Depends(get_current_user)],
)


class DeviceCommandRequest(BaseModel):
    value: float


def _serialize_device(device: Device) -> dict[str, object]:
    return {
        "id": device.id,
        "name": device.name,
        "device_type": device.device_type,
        "state": device.state,
        "updated_at": device.updated_at.isoformat(),
    }


@router.get("")
def list_devices(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    devices = db.query(Device).order_by(Device.id.asc()).all()
    return [_serialize_device(device) for device in devices]


@router.get("/{device_id}")
def get_device(device_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    device = db.query(Device).filter(Device.id == device_id).first()
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )
    return _serialize_device(device)


@router.post("/{device_id}/command")
def send_device_command(
    device_id: str,
    payload: DeviceCommandRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    device = db.query(Device).filter(Device.id == device_id).first()
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    request.app.state.mqtt_handler.publish_device_command(device_id, payload.value)
    return {"status": "queued", "device_id": device_id, "value": payload.value}
