from __future__ import annotations

from copy import deepcopy

from app.devices import DeviceRegistry


SCENES: dict[str, dict[str, float]] = {
    "day": {
        "ceiling_light": 1.0,
        "bedside_light": 0.0,
        "light_level": 100.0,
        "thermostat": 22.0,
        "tv_on": 0.0,
    },
    "night": {
        "ceiling_light": 0.0,
        "bedside_light": 1.0,
        "light_level": 10.0,
        "thermostat": 20.0,
        "tv_on": 0.0,
    },
    "away": {
        "ceiling_light": 0.0,
        "bedside_light": 0.0,
        "light_level": 0.0,
        "thermostat": 17.0,
        "tv_on": 0.0,
    },
    "movie": {
        "ceiling_light": 0.0,
        "bedside_light": 0.0,
        "light_level": 20.0,
        "thermostat": 22.0,
        "tv_on": 1.0,
    },
}


def get_scene_commands(scene_id: str) -> dict[str, float]:
    if scene_id not in SCENES:
        raise ValueError(f"Unknown scene: {scene_id}")
    return deepcopy(SCENES[scene_id])


def apply_scene(registry: DeviceRegistry, scene_id: str) -> dict[str, float]:
    scene_commands = get_scene_commands(scene_id)
    changes: dict[str, float] = {}

    for device_id, target_value in scene_commands.items():
        current_state = float(registry.get(device_id)["state"])
        if current_state == target_value:
            continue
        registry.set_state(device_id, target_value)
        changes[device_id] = target_value

    return changes
