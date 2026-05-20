from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from db.models import DeviceState


DEVICE_METADATA: dict[str, dict[str, str]] = {
    "motion_hall": {"name": "Motion Hall", "device_type": "binary"},
    "motion_living": {"name": "Motion Living", "device_type": "binary"},
    "temperature": {"name": "Temperature", "device_type": "float"},
    "light_level": {"name": "Light Level", "device_type": "float"},
    "ceiling_light": {"name": "Ceiling Light", "device_type": "binary"},
    "bedside_light": {"name": "Bedside Light", "device_type": "binary"},
    "thermostat": {"name": "Thermostat", "device_type": "float"},
    "tv_on": {"name": "TV Power", "device_type": "binary"},
}

DEFAULT_DEVICE_VALUES: dict[str, float] = {
    "motion_hall": 0.0,
    "motion_living": 0.0,
    "temperature": 22.0,
    "light_level": 50.0,
    "ceiling_light": 0.0,
    "bedside_light": 0.0,
    "thermostat": 22.0,
    "tv_on": 0.0,
}

MOTION_DEVICE_IDS = {"motion_hall", "motion_living"}


def _device_value(states: dict[str, DeviceState], device_id: str) -> float:
    state = states.get(device_id)
    if state is None:
        return DEFAULT_DEVICE_VALUES[device_id]

    return float(state.value)


def build_feature_vector(
    session: Session,
    last_motion_at: Optional[datetime] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Union[int, float]]:
    now = now or datetime.utcnow()
    states = {
        state.id: state
        for state in session.query(DeviceState)
        .filter(DeviceState.id.in_(tuple(DEFAULT_DEVICE_VALUES.keys())))
        .all()
    }

    motion_hall = int(_device_value(states, "motion_hall") > 0.0)
    motion_living = int(_device_value(states, "motion_living") > 0.0)
    tv_on = int(_device_value(states, "tv_on") > 0.0)

    if motion_hall or motion_living:
        minutes_idle = 0
    elif last_motion_at is None:
        minutes_idle = 0
    else:
        minutes_idle = max(0, int((now - last_motion_at).total_seconds() // 60))

    return {
        "hour_of_day": now.hour,
        "weekday": now.weekday(),
        "motion_hall": motion_hall,
        "motion_living": motion_living,
        "temperature": float(_device_value(states, "temperature")),
        "light_level": float(_device_value(states, "light_level")),
        "tv_on": tv_on,
        "minutes_idle": minutes_idle,
    }


def normalize_device_item(
    device_id: str,
    payload: dict[str, Any],
    state: Optional[DeviceState] = None,
) -> dict[str, Any]:
    metadata = DEVICE_METADATA.get(device_id, {})
    device_type = str(
        payload.get("device_type")
        or payload.get("type")
        or metadata.get("device_type")
        or "float"
    )
    updated_at = payload.get("updated_at")
    if state is not None:
        updated_at = state.updated_at.isoformat()

    return {
        "id": device_id,
        "name": str(payload.get("name") or metadata.get("name") or device_id),
        "device_type": device_type,
        "state": float(payload.get("state", payload.get("value", DEFAULT_DEVICE_VALUES.get(device_id, 0.0)))),
        "updated_at": str(updated_at or datetime.utcnow().isoformat()),
    }
