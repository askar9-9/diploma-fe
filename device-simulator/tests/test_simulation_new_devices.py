import asyncio
from unittest.mock import MagicMock

import pytest

from app.devices import DeviceRegistry
from app.simulation import DaySimulator


def test_solar_generation_peaks_at_1300() -> None:
    assert DaySimulator.solar_generation(13, 0) == pytest.approx(5000.0)


def test_hems_action_uses_night_tariff_rule() -> None:
    assert DaySimulator.hems_action(23, 50.0) == "charge"
    assert DaySimulator.hems_action(14, 50.0) == "discharge"
    assert DaySimulator.hems_action(14, DaySimulator.MIN_SOC) == "idle"


@pytest.mark.asyncio
async def test_hems_devices_update_on_tick() -> None:
    registry = DeviceRegistry()
    mqtt_client = MagicMock()
    sim = DaySimulator(registry, mqtt_client)

    await sim.start(speed=60)
    await asyncio.sleep(1.1)
    sim.stop()
    await asyncio.sleep(0.05)

    assert registry.get("solar_panel")["state"] == 0.0
    assert registry.get("battery_soc")["state"] == 75.0
    assert registry.get("grid_power")["state"] == 2800.0

    published_ids = {call.args[0] for call in mqtt_client.publish_state.call_args_list}
    assert {"solar_panel", "battery_soc", "grid_power"} <= published_ids
