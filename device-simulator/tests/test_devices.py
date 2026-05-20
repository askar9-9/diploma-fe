import pytest

from app.devices import DEVICE_POWER_KW, DeviceRegistry, get_active_load_kw


def test_initial_11_devices() -> None:
    registry = DeviceRegistry()

    assert len(registry.get_all()) == 11


def test_motion_hall_binary_initial() -> None:
    registry = DeviceRegistry()

    assert registry.get("motion_hall")["state"] == 0.0

def test_new_devices_initial() -> None:
    registry = DeviceRegistry()

    assert registry.get("solar_panel")["state"] == 0.0
    assert registry.get("battery_soc")["state"] == 50.0
    assert registry.get("grid_power")["state"] == 0.0


def test_set_state_binary() -> None:
    registry = DeviceRegistry()

    registry.set_state("motion_hall", 1.0)

    assert registry.get("motion_hall")["state"] == 1.0


def test_set_state_float() -> None:
    registry = DeviceRegistry()

    registry.set_state("temperature", 25.5)

    assert registry.get("temperature")["state"] == 25.5


def test_invalid_device_raises_keyerror() -> None:
    registry = DeviceRegistry()

    with pytest.raises(KeyError):
        registry.get("nonexistent")


def test_reset() -> None:
    registry = DeviceRegistry()
    registry.set_state("temperature", 25.5)

    registry.reset()

    assert registry.get("temperature")["state"] == 20.0


def test_get_active_load_kw_counts_active_consumers() -> None:
    registry = DeviceRegistry()
    registry.set_state("ceiling_light", 1.0)
    registry.set_state("thermostat", 22.0)
    registry.set_state("tv_on", 0.0)

    result = get_active_load_kw(registry)

    assert DEVICE_POWER_KW["ceiling_light"] == 0.06
    assert result == {
        "total_load_kw": 2.06,
        "by_device": {
            "ceiling_light": 0.06,
            "thermostat": 2.0,
        },
    }
