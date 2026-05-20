from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _format_numeric_state(value: float) -> str:
    text = f"{float(value):.3f}".rstrip("0").rstrip(".")
    if "." not in text:
        text = f"{text}.0"
    return text


def _normalize_state_value(device: dict[str, Any], value: object) -> str:
    sim_type = str(device.get("sim", {}).get("type", "")).lower()
    domain = str(device.get("domain", "")).lower()
    current_state = str(device.get("state", "")).strip().lower()
    is_binary = sim_type in {"binary", "always_on"} or current_state in {"on", "off"} or domain in {
        "binary_sensor",
        "switch",
        "light",
    }

    if is_binary:
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"on", "off"}:
                return lowered
            if lowered in {"1", "1.0", "true", "yes"}:
                return "on"
            if lowered in {"0", "0.0", "false", "no"}:
                return "off"
        elif isinstance(value, bool):
            return "on" if value else "off"
        else:
            try:
                return "on" if float(value) > 0.0 else "off"
            except (TypeError, ValueError):
                pass

    if isinstance(value, str):
        raw = value.strip()
        lowered = raw.lower()
        if lowered in {"on", "off"}:
            return lowered
        try:
            return _format_numeric_state(float(raw))
        except ValueError:
            return raw

    if isinstance(value, bool):
        return "on" if value else "off"

    try:
        return _format_numeric_state(float(value))
    except (TypeError, ValueError):
        return str(value)


def is_active_state(state: object) -> bool:
    if isinstance(state, str):
        lowered = state.strip().lower()
        if lowered == "on":
            return True
        if lowered == "off":
            return False
        try:
            return float(lowered) > 0.0
        except ValueError:
            return bool(lowered)

    try:
        return float(state) > 0.0
    except (TypeError, ValueError):
        return bool(state)


def state_as_float(state: object, default: float = 0.0) -> float:
    if isinstance(state, str):
        lowered = state.strip().lower()
        if lowered == "on":
            return 1.0
        if lowered == "off":
            return 0.0
        try:
            return float(lowered)
        except ValueError:
            return default

    try:
        return float(state)
    except (TypeError, ValueError):
        return default


ROOM_LABELS: dict[str, str] = {
    "hallway": "Прихожая",
    "living": "Гостиная",
    "kitchen": "Кухня",
    "bedroom": "Спальня",
    "bathroom": "Ванная",
    "outdoor": "Улица",
    "utility": "Котельная",
}


XIAOMI_DEVICES: dict[str, dict[str, Any]] = {
    "binary_sensor.motion_hallway": {
        "name": "Xiaomi Mi Motion Sensor 2",
        "model": "RTCGQ02LM",
        "domain": "binary_sensor",
        "room": "hallway",
        "state": "off",
        "power_kw": 0.0,
        "attributes": {"device_class": "motion"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-mi-motion-sensor-2",
        "sim": {"type": "binary", "on_prob": 0.1},
    },
    "binary_sensor.door_hallway": {
        "name": "Aqara Door and Window Sensor",
        "model": "MCCGQ11LM",
        "domain": "binary_sensor",
        "room": "hallway",
        "state": "off",
        "power_kw": 0.0,
        "attributes": {"device_class": "door"},
        "doc_url": "https://www.aqara.com/us/door_and_window_sensor.html",
        "sim": {"type": "binary", "on_prob": 0.05},
    },
    "switch.plug_light_hallway": {
        "name": "Xiaomi Mi Smart Plug 2",
        "model": "ZNCZ04LM",
        "domain": "switch",
        "room": "hallway",
        "state": "off",
        "power_kw": 0.04,
        "attributes": {"device_class": "plug"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2",
        "sim": {"type": "binary", "on_prob": 0.3},
    },
    "binary_sensor.motion_living": {
        "name": "Xiaomi Mi Motion Sensor 2",
        "model": "RTCGQ02LM",
        "domain": "binary_sensor",
        "room": "living",
        "state": "off",
        "power_kw": 0.0,
        "attributes": {"device_class": "motion"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-mi-motion-sensor-2",
        "sim": {"type": "binary", "on_prob": 0.2},
    },
    "light.ceiling_living": {
        "name": "Yeelight Smart LED Bulb 1S",
        "model": "YLDP15YL",
        "domain": "light",
        "room": "living",
        "state": "off",
        "power_kw": 0.008,
        "attributes": {"color_mode": "color_temp"},
        "doc_url": "https://www.yeelight.com/en_US/product/lemon-color",
        "sim": {"type": "binary", "on_prob": 0.4},
    },
    "switch.plug_tv_living": {
        "name": "Xiaomi Mi Smart Plug 2",
        "model": "ZNCZ04LM",
        "domain": "switch",
        "room": "living",
        "state": "off",
        "power_kw": 0.15,
        "attributes": {"device_class": "plug"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2",
        "sim": {"type": "binary", "on_prob": 0.25},
    },
    "sensor.light_level_living": {
        "name": "Xiaomi Mi Light Detection Sensor",
        "model": "GZCGQ01LM",
        "domain": "sensor",
        "room": "living",
        "state": "0.0",
        "power_kw": 0.0,
        "attributes": {
            "device_class": "illuminance",
            "unit_of_measurement": "lx",
        },
        "doc_url": "https://www.mi.com/global/",
        "sim": {"type": "float", "min": 0.0, "max": 1000.0, "step": 50.0},
    },
    "sensor.temperature_kitchen": {
        "name": "Aqara Temperature and Humidity Sensor",
        "model": "WSDCGQ11LM",
        "domain": "sensor",
        "room": "kitchen",
        "state": "21.0",
        "power_kw": 0.0,
        "attributes": {
            "device_class": "temperature",
            "unit_of_measurement": "°C",
        },
        "doc_url": "https://www.aqara.com/us/temperature_humidity_sensor.html",
        "sim": {"type": "float", "min": 18.0, "max": 28.0, "step": 0.5},
    },
    "sensor.humidity_kitchen": {
        "name": "Aqara Temperature and Humidity Sensor",
        "model": "WSDCGQ11LM",
        "domain": "sensor",
        "room": "kitchen",
        "state": "50.0",
        "power_kw": 0.0,
        "attributes": {
            "device_class": "humidity",
            "unit_of_measurement": "%",
        },
        "doc_url": "https://www.aqara.com/us/temperature_humidity_sensor.html",
        "sim": {"type": "float", "min": 30.0, "max": 80.0, "step": 2.0},
    },
    "switch.plug_kettle_kitchen": {
        "name": "Xiaomi Mi Smart Plug 2",
        "model": "ZNCZ04LM",
        "domain": "switch",
        "room": "kitchen",
        "state": "off",
        "power_kw": 2.2,
        "attributes": {"device_class": "plug"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2",
        "sim": {"type": "binary", "on_prob": 0.1},
    },
    "switch.plug_fridge_kitchen": {
        "name": "Xiaomi Mi Smart Plug 2",
        "model": "ZNCZ04LM",
        "domain": "switch",
        "room": "kitchen",
        "state": "on",
        "power_kw": 0.15,
        "attributes": {"device_class": "plug"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2",
        "sim": {"type": "always_on"},
    },
    "binary_sensor.smoke_kitchen": {
        "name": "Xiaomi Mi Smart Smoke Alarm",
        "model": "JTYJ-GD-01LM/BW",
        "domain": "binary_sensor",
        "room": "kitchen",
        "state": "off",
        "power_kw": 0.0,
        "attributes": {"device_class": "smoke"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-mi-smoke-alarm",
        "sim": {"type": "binary", "on_prob": 0.001},
    },
    "binary_sensor.motion_bedroom": {
        "name": "Xiaomi Mi Motion Sensor 2",
        "model": "RTCGQ02LM",
        "domain": "binary_sensor",
        "room": "bedroom",
        "state": "off",
        "power_kw": 0.0,
        "attributes": {"device_class": "motion"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-mi-motion-sensor-2",
        "sim": {"type": "binary", "on_prob": 0.15},
    },
    "light.bedside_bedroom": {
        "name": "Yeelight LED Bedside Lamp D2",
        "model": "YLCT01YL",
        "domain": "light",
        "room": "bedroom",
        "state": "off",
        "power_kw": 0.02,
        "attributes": {"color_mode": "color_temp"},
        "doc_url": "https://www.yeelight.com/en_US/product/lemon-color",
        "sim": {"type": "binary", "on_prob": 0.2},
    },
    "switch.plug_purifier_bedroom": {
        "name": "Xiaomi Mi Air Purifier 3H",
        "model": "AC-M6-SC",
        "domain": "switch",
        "room": "bedroom",
        "state": "off",
        "power_kw": 0.038,
        "attributes": {"device_class": "plug"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-mi-air-purifier-3h",
        "sim": {"type": "binary", "on_prob": 0.5},
    },
    "sensor.humidity_bathroom": {
        "name": "Aqara Temperature and Humidity Sensor",
        "model": "WSDCGQ11LM",
        "domain": "sensor",
        "room": "bathroom",
        "state": "60.0",
        "power_kw": 0.0,
        "attributes": {
            "device_class": "humidity",
            "unit_of_measurement": "%",
        },
        "doc_url": "https://www.aqara.com/us/temperature_humidity_sensor.html",
        "sim": {"type": "float", "min": 40.0, "max": 90.0, "step": 3.0},
    },
    "switch.plug_boiler_bathroom": {
        "name": "Xiaomi Mi Smart Plug 2",
        "model": "ZNCZ04LM",
        "domain": "switch",
        "room": "bathroom",
        "state": "off",
        "power_kw": 2.0,
        "attributes": {"device_class": "plug"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2",
        "sim": {"type": "binary", "on_prob": 0.15},
    },
    "binary_sensor.motion_outdoor": {
        "name": "Aqara Motion Sensor P1",
        "model": "MS-S02",
        "domain": "binary_sensor",
        "room": "outdoor",
        "state": "off",
        "power_kw": 0.0,
        "attributes": {"device_class": "motion"},
        "doc_url": "https://www.aqara.com/us/motion-sensor-p1.html",
        "sim": {"type": "binary", "on_prob": 0.05},
    },
    "light.outdoor_light": {
        "name": "Xiaomi Mi Smart Outdoor Light",
        "model": "MUE4115GL",
        "domain": "light",
        "room": "outdoor",
        "state": "off",
        "power_kw": 0.015,
        "attributes": {},
        "doc_url": "https://www.mi.com/global/",
        "sim": {"type": "binary", "on_prob": 0.3},
    },
    "climate.thermostat_main": {
        "name": "Xiaomi Smart Home Hub 2",
        "model": "ZNDMWG03LM",
        "domain": "climate",
        "room": "utility",
        "state": "20.0",
        "power_kw": 2.0,
        "attributes": {
            "device_class": "temperature",
            "unit_of_measurement": "°C",
            "min": 17,
            "max": 25,
        },
        "doc_url": "https://www.mi.com/global/",
        "sim": {"type": "float", "min": 17.0, "max": 25.0, "step": 0.5},
    },
    "sensor.solar_panel": {
        "name": "Xiaomi Solar Panel",
        "model": "BHR5164GL",
        "domain": "sensor",
        "room": "outdoor",
        "state": "0.0",
        "power_kw": 0.0,
        "attributes": {
            "device_class": "power",
            "unit_of_measurement": "kW",
        },
        "doc_url": "https://www.mi.com/global/",
        "sim": {"type": "solar"},
    },
    "sensor.battery_soc": {
        "name": "Xiaomi Smart Battery Pack",
        "model": "BHR5164GL",
        "domain": "sensor",
        "room": "utility",
        "state": "50.0",
        "power_kw": 0.0,
        "attributes": {
            "device_class": "battery",
            "unit_of_measurement": "%",
        },
        "doc_url": "https://www.mi.com/global/",
        "sim": {"type": "float", "min": 10.0, "max": 100.0, "step": 1.0},
    },
}


LEGACY_DEVICE_ALIASES: dict[str, str] = {
    "motion_hall": "binary_sensor.motion_hallway",
    "motion_living": "binary_sensor.motion_living",
    "temperature": "sensor.temperature_kitchen",
    "light_level": "sensor.light_level_living",
    "ceiling_light": "light.ceiling_living",
    "bedside_light": "light.bedside_bedroom",
    "thermostat": "climate.thermostat_main",
    "tv_on": "switch.plug_tv_living",
    "solar_panel": "sensor.solar_panel",
    "battery_soc": "sensor.battery_soc",
}


LEGACY_DEVICE_TYPES: dict[str, str] = {
    "motion_hall": "binary",
    "motion_living": "binary",
    "temperature": "float",
    "light_level": "float",
    "ceiling_light": "binary",
    "bedside_light": "binary",
    "thermostat": "float",
    "tv_on": "binary",
    "solar_panel": "float",
    "battery_soc": "float",
    "grid_power": "float",
}


def _normalize_device(entity_id: str, data: dict[str, Any]) -> dict[str, Any]:
    device = deepcopy(data)
    device["domain"] = str(device.get("domain") or entity_id.split(".", 1)[0])
    device["room"] = str(device.get("room", "utility"))
    device["state"] = _normalize_state_value(device, device.get("state", "off"))
    device["power_kw"] = float(device.get("power_kw", 0.0))
    device["attributes"] = deepcopy(device.get("attributes", {}))
    device["doc_url"] = str(device.get("doc_url", ""))
    device["sim"] = deepcopy(device.get("sim", {}))
    device["updated_at"] = str(device.get("updated_at") or _now_iso())
    return device


class DeviceRegistry:
    def __init__(self) -> None:
        self._devices: dict[str, dict[str, Any]] = {}
        self._load_initial()

    def _load_initial(self) -> None:
        self._devices = {}
        for entity_id, data in XIAOMI_DEVICES.items():
            self._devices[entity_id] = _normalize_device(entity_id, data)

    def get_all(self) -> dict[str, dict[str, Any]]:
        return deepcopy(self._devices)

    def get(self, entity_id: str) -> dict[str, Any]:
        if entity_id not in self._devices:
            raise KeyError(entity_id)
        return deepcopy(self._devices[entity_id])

    def set_state(self, entity_id: str, state: object) -> str:
        if entity_id not in self._devices:
            raise KeyError(entity_id)

        normalized_state = _normalize_state_value(self._devices[entity_id], state)
        self._devices[entity_id]["state"] = normalized_state
        self._devices[entity_id]["updated_at"] = _now_iso()
        return normalized_state

    def add_device(self, entity_id: str, data: dict[str, Any]) -> None:
        self._devices[entity_id] = _normalize_device(entity_id, data)

    def reset(self) -> None:
        self._load_initial()


def get_active_load_kw(
    registry: DeviceRegistry,
) -> dict[str, float | dict[str, float]]:
    by_device: dict[str, float] = {}
    total = 0.0

    for entity_id, device in registry.get_all().items():
        power_kw = float(device.get("power_kw", 0.0))
        if power_kw <= 0.0 or not is_active_state(device.get("state")):
            continue

        by_device[entity_id] = round(power_kw, 3)
        total += power_kw

    return {"total_load_kw": round(total, 3), "by_device": by_device}


def get_legacy_devices(
    registry: DeviceRegistry,
) -> dict[str, dict[str, float | str]]:
    legacy_devices: dict[str, dict[str, float | str]] = {}

    for legacy_id, entity_id in LEGACY_DEVICE_ALIASES.items():
        try:
            device = registry.get(entity_id)
        except KeyError:
            continue

        legacy_devices[legacy_id] = {
            "type": LEGACY_DEVICE_TYPES[legacy_id],
            "state": state_as_float(device.get("state")),
        }

    load_info = get_active_load_kw(registry)
    solar_kw = state_as_float(
        registry.get("sensor.solar_panel").get("state"),
    )
    grid_kw = max(0.0, float(load_info["total_load_kw"]) - solar_kw)
    legacy_devices["grid_power"] = {
        "type": LEGACY_DEVICE_TYPES["grid_power"],
        "state": round(grid_kw, 3),
    }

    return legacy_devices
