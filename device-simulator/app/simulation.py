from __future__ import annotations

import asyncio
import json
import logging
import math
import random
from datetime import datetime
from typing import TYPE_CHECKING, Any

from app.devices import state_as_float

if TYPE_CHECKING:
    from app.devices import DeviceRegistry
    from app.mqtt_client import MQTTClient


LOGGER = logging.getLogger(__name__)


def _format_numeric_state(value: float) -> str:
    text = f"{float(value):.3f}".rstrip("0").rstrip(".")
    if "." not in text:
        text = f"{text}.0"
    return text


class DaySimulator:
    PUBLISH_INTERVAL_SECONDS = 5.0
    SOLAR_PEAK_KW = 3.0
    SOLAR_START_HOUR = 6.0
    SOLAR_END_HOUR = 20.0

    def __init__(self, registry: DeviceRegistry, mqtt_client: MQTTClient) -> None:
        self._registry = registry
        self._mqtt_client = mqtt_client
        self._running = False
        self._stop_event: asyncio.Event | None = None
        self._task: asyncio.Task[None] | None = None
        now = datetime.now().astimezone()
        self._simulated_hour = now.hour
        self._simulated_minute = now.minute
        self._speed = 60

    def set_battery_cmd(self, cmd: str | float) -> None:
        target_soc = max(0.0, min(100.0, state_as_float(cmd, default=50.0)))
        new_state = self._registry.set_state("sensor.battery_soc", target_soc)
        attributes = dict(self._registry.get("sensor.battery_soc").get("attributes", {}))
        self._mqtt_client.publish_state("sensor.battery_soc", new_state, attributes)

    def set_ev_cmd(self, cmd: str | float) -> None:
        LOGGER.debug("Ignoring legacy ev_charger command: %s", cmd)

    @property
    def is_running(self) -> bool:
        return self._running

    async def start(self, speed: int = 60) -> None:
        if self._running:
            return

        now = datetime.now().astimezone()
        self._simulated_hour = now.hour
        self._simulated_minute = now.minute
        self._speed = max(1, speed)
        self._stop_event = asyncio.Event()
        self._running = True
        self._task = asyncio.create_task(self._run())

    def stop(self) -> None:
        self._running = False
        if self._stop_event is not None:
            self._stop_event.set()
        self._publish_status()

    def status(self) -> dict[str, object]:
        return {
            "running": self._running,
            "simulated_hour": self._simulated_hour,
            "simulated_minute": self._simulated_minute,
            "speed": self._speed,
        }

    @classmethod
    def solar_generation(cls, hour: int, minute: int) -> float:
        daytime_hour = hour + minute / 60.0
        if daytime_hour < cls.SOLAR_START_HOUR or daytime_hour >= cls.SOLAR_END_HOUR:
            return 0.0

        phase = math.pi * (
            (daytime_hour - cls.SOLAR_START_HOUR)
            / (cls.SOLAR_END_HOUR - cls.SOLAR_START_HOUR)
        )
        generation = cls.SOLAR_PEAK_KW * math.sin(phase)
        return max(0.0, round(generation, 2))

    def _publish_status(self) -> None:
        try:
            status = json.dumps(
                {
                    "time": f"{self._simulated_hour:02d}:{self._simulated_minute:02d}",
                    "running": self._running,
                    "speed": self._speed,
                }
            )
            self._mqtt_client.publish("homeiq/simulation/status", status)
        except Exception:
            LOGGER.debug("Unable to publish simulation status", exc_info=True)

    def _advance_simulated_time(self) -> None:
        total_minutes = (
            self._simulated_hour * 60 + self._simulated_minute + self._speed
        ) % (24 * 60)
        self._simulated_hour = total_minutes // 60
        self._simulated_minute = total_minutes % 60

    def _next_state(self, device: dict[str, Any]) -> str:
        sim = dict(device.get("sim", {}))
        sim_type = str(sim.get("type", "")).lower()

        if sim_type == "binary":
            on_prob = float(sim.get("on_prob", 0.5))
            return "on" if random.random() < on_prob else "off"

        if sim_type == "always_on":
            return "on"

        if sim_type == "float":
            current = state_as_float(device.get("state"))
            step = abs(float(sim.get("step", 1.0)))
            min_value = float(sim.get("min", current))
            max_value = float(sim.get("max", current))
            delta = step if random.random() < 0.5 else -step
            next_value = min(max(current + delta, min_value), max_value)
            return _format_numeric_state(next_value)

        if sim_type == "solar":
            solar_kw = self.solar_generation(self._simulated_hour, self._simulated_minute)
            return _format_numeric_state(solar_kw)

        return str(device.get("state", "off"))

    def _simulate_once(self) -> None:
        for entity_id, device in self._registry.get_all().items():
            current_state = str(device.get("state", "off"))
            next_state = self._next_state(device)
            if next_state == current_state:
                continue

            updated_state = self._registry.set_state(entity_id, next_state)
            attributes = dict(device.get("attributes", {}))
            self._mqtt_client.publish_state(entity_id, updated_state, attributes)

    async def _run(self) -> None:
        assert self._stop_event is not None

        try:
            self._simulate_once()
            self._publish_status()

            while not self._stop_event.is_set():
                try:
                    await asyncio.wait_for(
                        asyncio.shield(self._stop_event.wait()),
                        timeout=self.PUBLISH_INTERVAL_SECONDS,
                    )
                    break
                except asyncio.TimeoutError:
                    pass

                self._advance_simulated_time()
                self._simulate_once()
                self._publish_status()
        except Exception as exc:
            LOGGER.error("DaySimulator background task error: %s", exc)
        finally:
            self._running = False
            self._publish_status()
