import asyncio
from unittest.mock import Mock

import pytest

from app.mqtt_client import MQTTClient


def test_home_battery_command_maps_to_battery_soc() -> None:
    on_device_command = Mock()
    mqtt_client = MQTTClient(on_device_command=on_device_command)

    mqtt_client._handle_command(
        "homeiq/devices/home_battery/command",
        {"state": 72.5},
    )

    on_device_command.assert_called_once_with("battery_soc", 72.5)


class AsyncSimulator:
    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.speed = 0

    async def start(self, speed: int = 1) -> None:
        self.started = True
        self.speed = speed

    def stop(self) -> None:
        self.stopped = True


@pytest.mark.asyncio
async def test_simulation_control_dispatches_to_simulator() -> None:
    mqtt_client = MQTTClient()
    simulator = AsyncSimulator()
    mqtt_client.set_simulator(simulator)

    mqtt_client._handle_simulation_control({"action": "start", "speed": 15})
    await asyncio.sleep(0.01)
    mqtt_client._handle_simulation_control({"action": "stop"})

    assert simulator.started is True
    assert simulator.speed == 15
    assert simulator.stopped is True
