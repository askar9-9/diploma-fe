import pytest

from app.devices import DeviceRegistry


def test_initial_8_devices() -> None:
    registry = DeviceRegistry()

    assert len(registry.get_all()) == 8


def test_motion_hall_binary_initial() -> None:
    registry = DeviceRegistry()

    assert registry.get("motion_hall")["state"] == 0.0


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
