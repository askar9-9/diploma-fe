import pytest

from app.devices import DeviceRegistry
from app.scenes import apply_scene, get_scene_commands


def test_day_ceiling_on() -> None:
    assert get_scene_commands("day")["ceiling_light"] == 1.0


def test_day_battery_target_metadata() -> None:
    assert get_scene_commands("day")["battery_target"] == 80.0


def test_night_bedside_on() -> None:
    assert get_scene_commands("night")["bedside_light"] == 1.0


def test_away_thermostat() -> None:
    assert get_scene_commands("away")["thermostat"] == 17.0


def test_movie_tv_on() -> None:
    assert get_scene_commands("movie")["tv_on"] == 1.0


def test_invalid_scene() -> None:
    with pytest.raises(ValueError):
        get_scene_commands("nonexistent")


def test_apply_scene_day() -> None:
    registry = DeviceRegistry()

    applied = apply_scene(registry, "day")

    assert registry.get("ceiling_light")["state"] == 1.0
    assert registry.get("battery_soc")["state"] == 50.0
    assert "battery_target" not in applied
