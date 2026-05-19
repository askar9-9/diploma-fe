from __future__ import annotations

import asyncio
import logging
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.devices import DeviceRegistry
    from app.mqtt_client import MQTTClient


LOGGER = logging.getLogger(__name__)

# Sensor states per hour range: (motion_hall, motion_living, temperature, light_level, tv_on)
_DAY_PROFILE: list[tuple[int, int, float, float, int]] = [
    # hour_start, hour_end (inclusive), motion_hall, motion_living, temperature, light_level, tv_on
]

# Profile entries: (hour_min, hour_max_inclusive, motion_hall, motion_living, temperature, light_level, tv_on)
_HOUR_PROFILES: list[tuple[int, int, int, int, float, float, int]] = [
    (0,  6,  0, 0, 19.0,  5.0, 0),   # night
    (7,  8,  1, 0, 21.0, 80.0, 0),   # morning
    (9,  17, 0, 0, 18.0, 100.0, 0),  # day/away
    (18, 21, 1, 1, 22.0, 60.0, 0),   # evening
    (22, 23, 0, 1, 21.0, 20.0, 1),   # movie/night
]


def _profile_for_hour(hour: int) -> tuple[int, int, float, float, int]:
    """Return (motion_hall, motion_living, temperature, light_level, tv_on) for the given hour."""
    for h_min, h_max, motion_hall, motion_living, temperature, light_level, tv_on in _HOUR_PROFILES:
        if h_min <= hour <= h_max:
            return motion_hall, motion_living, temperature, light_level, tv_on
    # Fallback to night profile
    return 0, 0, 19.0, 5.0, 0


def _apply_noise(
    motion_hall: int,
    motion_living: int,
    temperature: float,
    light_level: float,
    tv_on: int,
) -> tuple[int, int, float, float, int]:
    """Apply random noise: temperature ±1.0, light_level ±5.0, 5% motion bit flip."""
    noisy_temperature = temperature + random.uniform(-1.0, 1.0)
    noisy_light_level = max(0.0, min(100.0, light_level + random.uniform(-5.0, 5.0)))
    noisy_motion_hall = motion_hall ^ 1 if random.random() < 0.05 else motion_hall
    noisy_motion_living = motion_living ^ 1 if random.random() < 0.05 else motion_living
    return noisy_motion_hall, noisy_motion_living, noisy_temperature, noisy_light_level, tv_on


class DaySimulator:
    def __init__(self, registry: DeviceRegistry, mqtt_client: MQTTClient) -> None:
        self._registry = registry
        self._mqtt_client = mqtt_client
        self._running = False
        self._stop_event: asyncio.Event | None = None
        self._task: asyncio.Task | None = None  # type: ignore[type-arg]
        self._simulated_hour: int = 0
        self._simulated_minute: int = 0
        self._speed: int = 1

    @property
    def is_running(self) -> bool:
        return self._running

    async def start(self, speed: int = 1) -> None:
        if self._running:
            return
        self._speed = max(1, speed)
        self._simulated_hour = 0
        self._simulated_minute = 0
        self._stop_event = asyncio.Event()
        self._running = True
        self._task = asyncio.create_task(self._run())

    def stop(self) -> None:
        self._running = False
        if self._stop_event is not None:
            self._stop_event.set()

    def status(self) -> dict[str, object]:
        return {
            "running": self._running,
            "simulated_hour": self._simulated_hour,
            "simulated_minute": self._simulated_minute,
            "speed": self._speed,
        }

    def _publish_hour_profile(self, hour: int) -> None:
        motion_hall, motion_living, temperature, light_level, tv_on = _profile_for_hour(hour)
        motion_hall, motion_living, temperature, light_level, tv_on = _apply_noise(
            motion_hall, motion_living, temperature, light_level, tv_on
        )

        updates = {
            "motion_hall": float(motion_hall),
            "motion_living": float(motion_living),
            "temperature": temperature,
            "light_level": light_level,
            "tv_on": float(tv_on),
        }

        for device_id, value in updates.items():
            try:
                self._registry.set_state(device_id, value)
                self._mqtt_client.publish_state(device_id, value)
            except Exception as exc:
                LOGGER.error("DaySimulator: failed to update %s: %s", device_id, exc)

    async def _run(self) -> None:
        assert self._stop_event is not None

        last_published_hour: int | None = None

        try:
            while not self._stop_event.is_set():
                current_hour = self._simulated_hour

                if current_hour != last_published_hour:
                    self._publish_hour_profile(current_hour)
                    last_published_hour = current_hour

                # Wait 1 real second, but check stop event
                try:
                    await asyncio.wait_for(
                        asyncio.shield(self._stop_event.wait()), timeout=1.0
                    )
                    # stop_event was set
                    break
                except asyncio.TimeoutError:
                    pass

                # Advance simulated time by `speed` minutes
                total_minutes = self._simulated_hour * 60 + self._simulated_minute + self._speed
                total_minutes %= 24 * 60  # wrap around at end of day
                self._simulated_hour = total_minutes // 60
                self._simulated_minute = total_minutes % 60

        except Exception as exc:
            LOGGER.error("DaySimulator background task error: %s", exc)
        finally:
            self._running = False
