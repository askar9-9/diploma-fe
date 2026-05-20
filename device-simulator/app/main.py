from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app.devices import (
    LEGACY_DEVICE_ALIASES,
    ROOM_LABELS,
    DeviceRegistry,
    get_active_load_kw,
    get_legacy_devices,
    state_as_float,
)
from app.mqtt_client import MQTTClient
from app.scenes import apply_scene
from app.simulation import DaySimulator


LOGGER = logging.getLogger(__name__)

app = FastAPI(title="HomeIQ Device Simulator")
registry = DeviceRegistry()
simulated_time: datetime | None = None


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _resolve_entity_id(device_ref: str) -> str:
    if device_ref in LEGACY_DEVICE_ALIASES:
        return LEGACY_DEVICE_ALIASES[device_ref]

    registry.get(device_ref)
    return device_ref


def _entity_response(entity_id: str, device: dict[str, Any]) -> dict[str, Any]:
    room = str(device.get("room", "utility"))
    return {
        "entity_id": entity_id,
        "name": str(device.get("name", entity_id)),
        "model": str(device.get("model", "")),
        "domain": str(device.get("domain", entity_id.split(".", 1)[0])),
        "room": room,
        "room_ru": ROOM_LABELS.get(room, room),
        "state": str(device.get("state", "off")),
        "attributes": dict(device.get("attributes", {})),
        "doc_url": str(device.get("doc_url", "")),
        "power_kw": float(device.get("power_kw", 0.0)),
        "updated_at": str(device.get("updated_at", _now_iso())),
    }


def _default_state_for_domain(domain: str) -> str:
    if domain in {"binary_sensor", "switch", "light"}:
        return "off"
    return "0.0"


def _default_sim_for_domain(domain: str) -> dict[str, Any]:
    if domain in {"binary_sensor", "switch", "light"}:
        return {"type": "binary", "on_prob": 0.1}
    return {"type": "float", "min": 0.0, "max": 100.0, "step": 1.0}


def _apply_device_state(
    device_ref: str,
    value: str | float | int,
    *,
    publish: bool = True,
) -> tuple[str, dict[str, Any]]:
    entity_id = _resolve_entity_id(device_ref)
    registry.set_state(entity_id, value)
    device = registry.get(entity_id)

    if publish:
        mqtt_client.publish_state(
            entity_id,
            str(device["state"]),
            dict(device.get("attributes", {})),
        )

    return entity_id, device


def _activate_scene(scene_id: str, *, publish: bool = True) -> dict[str, str]:
    applied = apply_scene(registry, scene_id)

    if publish:
        for entity_id, state in applied.items():
            device = registry.get(entity_id)
            mqtt_client.publish_state(
                entity_id,
                state,
                dict(device.get("attributes", {})),
            )
        mqtt_client.publish_scene_confirmed(scene_id)

    return applied


def _handle_device_command(entity_id: str, state: str) -> None:
    try:
        if entity_id in {"sensor.battery_soc", "battery_soc", "home_battery"}:
            simulator.set_battery_cmd(state)
        elif entity_id == "ev_charger":
            simulator.set_ev_cmd(state)
        else:
            _apply_device_state(entity_id, state, publish=True)
    except KeyError:
        LOGGER.warning("Ignoring MQTT command for unknown entity: %s", entity_id)


def _handle_scene_activate(scene_id: str) -> None:
    try:
        _activate_scene(scene_id, publish=True)
    except ValueError:
        LOGGER.warning("Ignoring MQTT activation for unknown scene: %s", scene_id)


def _publish_initial_states() -> None:
    for entity_id, device in registry.get_all().items():
        mqtt_client.publish_state(
            entity_id,
            str(device.get("state", "off")),
            dict(device.get("attributes", {})),
        )


mqtt_client = MQTTClient(
    on_device_command=_handle_device_command,
    on_scene_activate=_handle_scene_activate,
    on_connected=_publish_initial_states,
)

simulator = DaySimulator(registry=registry, mqtt_client=mqtt_client)


class LegacyDeviceStateUpdate(BaseModel):
    value: str | float | int


class EntityCommandRequest(BaseModel):
    state: str | float | int


class CreateEntityRequest(BaseModel):
    entity_id: str
    name: str
    model: str
    domain: str
    room: str
    doc_url: str
    state: str | float | int | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    power_kw: float = 0.0
    sim: dict[str, Any] | None = None


class TimeUpdate(BaseModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)


class SimulationStartRequest(BaseModel):
    speed: int = Field(default=60, ge=1, description="Simulated minutes per 5-second cycle")


@app.on_event("startup")
async def on_startup() -> None:
    mqtt_client.set_simulator(simulator)
    mqtt_client.connect()


@app.on_event("shutdown")
def on_shutdown() -> None:
    simulator.stop()
    mqtt_client.disconnect()


@app.get("/health")
def get_health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/devices")
def get_devices() -> dict[str, dict[str, float | str]]:
    return get_legacy_devices(registry)


@app.get("/entities")
def get_entities() -> list[dict[str, Any]]:
    entities = [
        _entity_response(entity_id, device)
        for entity_id, device in sorted(registry.get_all().items())
    ]
    return entities


@app.post("/entities", status_code=status.HTTP_201_CREATED)
def create_entity(payload: CreateEntityRequest) -> dict[str, Any]:
    if "." not in payload.entity_id:
        raise HTTPException(
            status_code=400,
            detail="entity_id must be in Home Assistant format: domain.name",
        )

    domain_from_id, _ = payload.entity_id.split(".", 1)
    if domain_from_id != payload.domain:
        raise HTTPException(
            status_code=400,
            detail="entity_id domain must match payload.domain",
        )

    try:
        registry.get(payload.entity_id)
    except KeyError:
        pass
    else:
        raise HTTPException(status_code=409, detail=f"Entity already exists: {payload.entity_id}")

    data = {
        "name": payload.name,
        "model": payload.model,
        "domain": payload.domain,
        "room": payload.room,
        "state": payload.state if payload.state is not None else _default_state_for_domain(payload.domain),
        "power_kw": payload.power_kw,
        "attributes": payload.attributes,
        "doc_url": payload.doc_url,
        "sim": payload.sim if payload.sim is not None else _default_sim_for_domain(payload.domain),
    }
    registry.add_device(payload.entity_id, data)
    device = registry.get(payload.entity_id)
    mqtt_client.publish_state(
        payload.entity_id,
        str(device.get("state", "off")),
        dict(device.get("attributes", {})),
    )
    return _entity_response(payload.entity_id, device)


@app.get("/entities/{entity_id}")
def get_entity(entity_id: str) -> dict[str, Any]:
    try:
        return _entity_response(entity_id, registry.get(entity_id))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown entity: {entity_id}") from exc


@app.post("/entities/{entity_id}/command")
def command_entity(entity_id: str, payload: EntityCommandRequest) -> dict[str, Any]:
    try:
        resolved_entity_id, device = _apply_device_state(entity_id, payload.state, publish=True)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown entity: {entity_id}") from exc

    return _entity_response(resolved_entity_id, device)


@app.get("/devices/energy")
def get_energy_summary() -> dict[str, float | dict[str, float]]:
    load_info = get_active_load_kw(registry)
    total_load_kw = float(load_info["total_load_kw"])
    by_device = dict(load_info["by_device"])

    def safe_float(entity_id: str, default: float = 0.0) -> float:
        try:
            device = registry.get(entity_id)
            return state_as_float(device.get("state"), default)
        except KeyError:
            return default

    solar_kw = safe_float("sensor.solar_panel")
    battery_soc_pct = safe_float("sensor.battery_soc")
    grid_kw = max(0.0, total_load_kw - solar_kw)

    return {
        "total_load_kw": round(total_load_kw, 3),
        "solar_kw": round(solar_kw, 3),
        "grid_kw": round(grid_kw, 3),
        "battery_soc_pct": round(battery_soc_pct, 1),
        "by_device": by_device,
    }


@app.get("/devices/{device_id}")
def get_device(device_id: str) -> dict[str, float | str]:
    legacy_devices = get_legacy_devices(registry)
    if device_id in legacy_devices:
        return legacy_devices[device_id]

    try:
        entity_id = _resolve_entity_id(device_id)
        device = registry.get(entity_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown device: {device_id}") from exc

    return {"type": "float", "state": state_as_float(device.get("state"))}


@app.post("/devices/{device_id}/state")
def update_device_state(
    device_id: str,
    payload: LegacyDeviceStateUpdate,
) -> dict[str, float | str]:
    try:
        _apply_device_state(device_id, payload.value, publish=True)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown device: {device_id}") from exc

    legacy_devices = get_legacy_devices(registry)
    if device_id in legacy_devices:
        return legacy_devices[device_id]

    resolved_entity_id = _resolve_entity_id(device_id)
    device = registry.get(resolved_entity_id)
    return {"type": "float", "state": state_as_float(device.get("state"))}


@app.post("/scenes/{scene_id}/activate")
def activate_scene(scene_id: str) -> dict[str, object]:
    try:
        applied = _activate_scene(scene_id, publish=True)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown scene: {scene_id}") from exc
    return {"scene": scene_id, "applied": applied}


@app.get("/time")
def get_time() -> dict[str, str | None]:
    return {
        "simulated_time": simulated_time.isoformat() if simulated_time is not None else None,
        "real_time": _now_iso(),
    }


@app.post("/time")
def set_time(payload: TimeUpdate) -> dict[str, str]:
    global simulated_time

    simulated_time = datetime.now().astimezone().replace(
        hour=payload.hour,
        minute=payload.minute,
        second=0,
        microsecond=0,
    )
    return {
        "simulated_time": simulated_time.isoformat(),
        "real_time": _now_iso(),
    }


@app.post("/simulation/start")
async def start_simulation(payload: SimulationStartRequest) -> dict[str, object]:
    await simulator.start(speed=payload.speed)
    return simulator.status()


@app.post("/simulation/stop")
def stop_simulation() -> dict[str, object]:
    simulator.stop()
    return simulator.status()


@app.get("/simulation/status")
def get_simulation_status() -> dict[str, object]:
    return simulator.status()
