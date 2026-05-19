from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.devices import DeviceRegistry
from app.mqtt_client import MQTTClient
from app.scenes import apply_scene
from app.simulation import DaySimulator


app = FastAPI(title="HomeIQ Device Simulator")
registry = DeviceRegistry()
simulated_time: datetime | None = None


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _set_device_state(device_id: str, value: float, publish: bool = True) -> dict[str, float | str]:
    try:
        registry.set_state(device_id, value)
        device = registry.get(device_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown device: {device_id}") from exc

    if publish:
        mqtt_client.publish_state(device_id, float(device["state"]))

    return device


def _activate_scene(scene_id: str, publish: bool = True) -> dict[str, float]:
    try:
        applied = apply_scene(registry, scene_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown scene: {scene_id}") from exc

    if publish:
        for device_id, value in applied.items():
            mqtt_client.publish_state(device_id, value)
        mqtt_client.publish_scene_confirmed(scene_id)

    return applied


def _handle_device_command(device_id: str, value: float) -> None:
    _set_device_state(device_id, value, publish=True)


def _handle_scene_activate(scene_id: str) -> None:
    _activate_scene(scene_id, publish=True)


def _publish_initial_states() -> None:
    for device_id, device in registry.get_all().items():
        mqtt_client.publish_state(device_id, float(device["state"]))


mqtt_client = MQTTClient(
    on_device_command=_handle_device_command,
    on_scene_activate=_handle_scene_activate,
    on_connected=_publish_initial_states,
)

simulator = DaySimulator(registry=registry, mqtt_client=mqtt_client)


class DeviceStateUpdate(BaseModel):
    value: float


class TimeUpdate(BaseModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)


class SimulationStartRequest(BaseModel):
    speed: int = Field(default=60, ge=1, description="Simulated minutes per real second")


@app.on_event("startup")
def on_startup() -> None:
    mqtt_client.connect()


@app.on_event("shutdown")
def on_shutdown() -> None:
    mqtt_client.disconnect()


@app.get("/health")
def get_health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/devices")
def get_devices() -> dict[str, dict[str, float | str]]:
    return registry.get_all()


@app.get("/devices/{device_id}")
def get_device(device_id: str) -> dict[str, float | str]:
    try:
        return registry.get(device_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown device: {device_id}") from exc


@app.post("/devices/{device_id}/state")
def update_device_state(
    device_id: str, payload: DeviceStateUpdate
) -> dict[str, float | str]:
    return _set_device_state(device_id, payload.value, publish=True)


@app.post("/scenes/{scene_id}/activate")
def activate_scene(scene_id: str) -> dict[str, object]:
    applied = _activate_scene(scene_id, publish=True)
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
