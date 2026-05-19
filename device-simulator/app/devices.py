from __future__ import annotations

from copy import deepcopy


INITIAL_DEVICES: dict[str, dict[str, float | str]] = {
    "motion_hall": {"type": "binary", "state": 0.0},
    "motion_living": {"type": "binary", "state": 0.0},
    "temperature": {"type": "float", "state": 20.0},
    "light_level": {"type": "float", "state": 0.0},
    "ceiling_light": {"type": "binary", "state": 0.0},
    "bedside_light": {"type": "binary", "state": 0.0},
    "thermostat": {"type": "float", "state": 20.0},
    "tv_on": {"type": "binary", "state": 0.0},
}


class DeviceRegistry:
    def __init__(self) -> None:
        self._initial_devices = deepcopy(INITIAL_DEVICES)
        self._devices = deepcopy(INITIAL_DEVICES)

    def get_all(self) -> dict[str, dict[str, float | str]]:
        return deepcopy(self._devices)

    def get(self, device_id: str) -> dict[str, float | str]:
        if device_id not in self._devices:
            raise KeyError(device_id)
        return deepcopy(self._devices[device_id])

    def set_state(self, device_id: str, value: float) -> float:
        if device_id not in self._devices:
            raise KeyError(device_id)

        state = float(value)
        self._devices[device_id]["state"] = state
        return state

    def reset(self) -> None:
        self._devices = deepcopy(self._initial_devices)
