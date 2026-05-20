from __future__ import annotations

from copy import deepcopy

from app.devices import DeviceRegistry


SCENES: dict[str, dict[str, str]] = {
    "day": {
        "light.ceiling_living": "on",
        "light.bedside_bedroom": "off",
        "sensor.light_level_living": "100.0",
        "climate.thermostat_main": "22.0",
        "switch.plug_tv_living": "off",
        "battery_target": "80.0",
    },
    "night": {
        "light.ceiling_living": "off",
        "light.bedside_bedroom": "on",
        "sensor.light_level_living": "10.0",
        "climate.thermostat_main": "20.0",
        "switch.plug_tv_living": "off",
        "battery_target": "30.0",
    },
    "away": {
        "light.ceiling_living": "off",
        "light.bedside_bedroom": "off",
        "sensor.light_level_living": "0.0",
        "climate.thermostat_main": "17.0",
        "switch.plug_tv_living": "off",
        "battery_target": "50.0",
    },
    "movie": {
        "light.ceiling_living": "off",
        "light.bedside_bedroom": "off",
        "sensor.light_level_living": "20.0",
        "climate.thermostat_main": "22.0",
        "switch.plug_tv_living": "on",
        "battery_target": "60.0",
    },
}

_SCENE_METADATA_KEYS = {"battery_target"}


def get_scene_commands(scene_id: str) -> dict[str, str]:
    if scene_id not in SCENES:
        raise ValueError(f"Unknown scene: {scene_id}")
    return deepcopy(SCENES[scene_id])


def apply_scene(registry: DeviceRegistry, scene_id: str) -> dict[str, str]:
    scene_commands = get_scene_commands(scene_id)
    changes: dict[str, str] = {}

    for entity_id, target_state in scene_commands.items():
        if entity_id in _SCENE_METADATA_KEYS:
            continue
        current_state = str(registry.get(entity_id)["state"])
        if current_state == target_state:
            continue
        registry.set_state(entity_id, target_state)
        changes[entity_id] = target_state

    return changes
