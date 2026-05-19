from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from app.devices import DeviceRegistry
from app.simulation import DaySimulator, _apply_noise, _profile_for_hour


# ---------------------------------------------------------------------------
# Unit tests for _profile_for_hour
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "hour,expected_motion_hall,expected_motion_living,expected_tv_on",
    [
        (0,  0, 0, 0),   # night start
        (3,  0, 0, 0),   # middle of night
        (6,  0, 0, 0),   # night end
        (7,  1, 0, 0),   # morning start
        (8,  1, 0, 0),   # morning end
        (9,  0, 0, 0),   # day/away start
        (13, 0, 0, 0),   # midday
        (17, 0, 0, 0),   # day/away end
        (18, 1, 1, 0),   # evening start
        (20, 1, 1, 0),   # evening
        (21, 1, 1, 0),   # evening end
        (22, 0, 1, 1),   # movie/night start
        (23, 0, 1, 1),   # movie/night end
    ],
)
def test_profile_for_hour_motion_and_tv(
    hour: int,
    expected_motion_hall: int,
    expected_motion_living: int,
    expected_tv_on: int,
) -> None:
    motion_hall, motion_living, _temperature, _light_level, tv_on = _profile_for_hour(hour)
    assert motion_hall == expected_motion_hall, f"hour={hour}: motion_hall mismatch"
    assert motion_living == expected_motion_living, f"hour={hour}: motion_living mismatch"
    assert tv_on == expected_tv_on, f"hour={hour}: tv_on mismatch"


@pytest.mark.parametrize(
    "hour,expected_temperature,expected_light_level",
    [
        (3,  19.0,  5.0),   # night
        (7,  21.0, 80.0),   # morning
        (12, 18.0, 100.0),  # day/away
        (19, 22.0, 60.0),   # evening
        (23, 21.0, 20.0),   # movie/night
    ],
)
def test_profile_for_hour_temperature_and_light(
    hour: int,
    expected_temperature: float,
    expected_light_level: float,
) -> None:
    _mh, _ml, temperature, light_level, _tv = _profile_for_hour(hour)
    assert temperature == pytest.approx(expected_temperature)
    assert light_level == pytest.approx(expected_light_level)


# ---------------------------------------------------------------------------
# Unit tests for _apply_noise
# ---------------------------------------------------------------------------

def test_apply_noise_temperature_range() -> None:
    for _ in range(100):
        _, _, temp, _, _ = _apply_noise(0, 0, 20.0, 50.0, 0)
        assert 19.0 <= temp <= 21.0, f"temperature {temp} out of expected range"


def test_apply_noise_light_level_clamped() -> None:
    for _ in range(100):
        _, _, _, light, _ = _apply_noise(0, 0, 20.0, 0.0, 0)
        assert light >= 0.0, f"light_level {light} is negative"

    for _ in range(100):
        _, _, _, light, _ = _apply_noise(0, 0, 20.0, 100.0, 0)
        assert light <= 100.0, f"light_level {light} exceeds 100"


def test_apply_noise_tv_unchanged() -> None:
    for _ in range(50):
        _, _, _, _, tv = _apply_noise(0, 0, 20.0, 50.0, 1)
        assert tv == 1
    for _ in range(50):
        _, _, _, _, tv = _apply_noise(0, 0, 20.0, 50.0, 0)
        assert tv == 0


# ---------------------------------------------------------------------------
# DaySimulator: start / stop state
# ---------------------------------------------------------------------------

def _make_simulator() -> tuple[DaySimulator, MagicMock, DeviceRegistry]:
    registry = DeviceRegistry()
    mqtt_client = MagicMock()
    sim = DaySimulator(registry=registry, mqtt_client=mqtt_client)
    return sim, mqtt_client, registry


def test_simulator_initially_not_running() -> None:
    sim, _, _ = _make_simulator()
    assert sim.is_running is False


@pytest.mark.asyncio
async def test_simulator_start_sets_running() -> None:
    sim, _, _ = _make_simulator()
    await sim.start(speed=60)
    assert sim.is_running is True
    sim.stop()
    # Give the background task a moment to finish
    await asyncio.sleep(0.05)


@pytest.mark.asyncio
async def test_simulator_stop_clears_running() -> None:
    sim, _, _ = _make_simulator()
    await sim.start(speed=60)
    sim.stop()
    await asyncio.sleep(0.05)
    assert sim.is_running is False


@pytest.mark.asyncio
async def test_simulator_start_twice_is_idempotent() -> None:
    sim, _, _ = _make_simulator()
    await sim.start(speed=60)
    await sim.start(speed=120)  # second call should be ignored
    assert sim._speed == 60  # speed should remain from first call
    sim.stop()
    await asyncio.sleep(0.05)


# ---------------------------------------------------------------------------
# DaySimulator: status
# ---------------------------------------------------------------------------

def test_simulator_status_when_stopped() -> None:
    sim, _, _ = _make_simulator()
    status = sim.status()
    assert status["running"] is False
    assert status["simulated_hour"] == 0
    assert status["simulated_minute"] == 0


@pytest.mark.asyncio
async def test_simulator_status_when_running() -> None:
    sim, _, _ = _make_simulator()
    await sim.start(speed=30)
    status = sim.status()
    assert status["running"] is True
    assert status["speed"] == 30
    sim.stop()
    await asyncio.sleep(0.05)


# ---------------------------------------------------------------------------
# DaySimulator: MQTT publishing
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_simulator_publishes_on_hour_change() -> None:
    sim, mqtt_client, _ = _make_simulator()
    await sim.start(speed=60)
    # Wait long enough for at least one publish cycle (1 second tick)
    await asyncio.sleep(1.1)
    sim.stop()
    await asyncio.sleep(0.05)

    # Should have called publish_state for sensor devices
    published_ids = {call.args[0] for call in mqtt_client.publish_state.call_args_list}
    assert "temperature" in published_ids
    assert "light_level" in published_ids
    assert "motion_hall" in published_ids
    assert "motion_living" in published_ids
    assert "tv_on" in published_ids


@pytest.mark.asyncio
async def test_simulator_updates_registry() -> None:
    sim, _, registry = _make_simulator()
    await sim.start(speed=1)
    await asyncio.sleep(0.1)  # Let one publish happen immediately (hour 0)
    sim.stop()
    await asyncio.sleep(0.05)

    # At hour 0 (night profile): motion_hall=0, motion_living=0, tv_on=0
    # temperature ~19.0, light_level ~5.0
    temp = float(registry.get("temperature")["state"])
    assert 18.0 <= temp <= 20.0, f"temperature {temp} unexpected for night profile"
