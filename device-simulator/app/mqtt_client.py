from __future__ import annotations

import asyncio
import inspect
import json
import logging
import os
from datetime import datetime
from typing import Any, Callable

import paho.mqtt.client as mqtt


LOGGER = logging.getLogger(__name__)


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat()


class MQTTClient:
    def __init__(
        self,
        on_device_command: Callable[[str, str], None] | None = None,
        on_scene_activate: Callable[[str], None] | None = None,
        on_connected: Callable[[], None] | None = None,
        host: str | None = None,
        port: int | None = None,
    ) -> None:
        self.host = host or os.getenv("MQTT_HOST", "mosquitto")
        self.port = int(port or os.getenv("MQTT_PORT", "1883"))
        self.on_device_command = on_device_command
        self.on_scene_activate = on_scene_activate
        self.on_connected = on_connected
        self._simulator = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def connect(self) -> bool:
        try:
            self.client.reconnect_delay_set(min_delay=1, max_delay=10)
            self.client.connect_async(self.host, self.port, keepalive=60)
            self.client.loop_start()
            return True
        except Exception as exc:  # pragma: no cover - depends on runtime broker
            LOGGER.error(
                "Unable to connect to MQTT broker at %s:%s: %s",
                self.host,
                self.port,
                exc,
            )
            return False

    def disconnect(self) -> None:
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception as exc:  # pragma: no cover - defensive cleanup
            LOGGER.error("Unable to disconnect MQTT client cleanly: %s", exc)

    def publish_state(
        self,
        entity_id: str,
        state: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        domain, entity_name = entity_id.split(".", 1)
        payload = json.dumps(
            {"state": state, "attributes": attributes or {}},
            ensure_ascii=False,
        )
        self._publish(
            f"homeiq/{domain}/{entity_name}/state",
            payload,
            retain=True,
        )

    def publish_scene_confirmed(self, scene_id: str) -> None:
        payload = json.dumps({"scene": scene_id, "timestamp": _timestamp()})
        self._publish("homeiq/scenes/confirmed", payload, retain=False)

    def publish(self, topic: str, payload: str, retain: bool = False) -> None:
        self._publish(topic, payload, retain=retain)

    def set_simulator(self, simulator: object) -> None:
        self._simulator = simulator
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

    def _publish(self, topic: str, payload: str, retain: bool) -> None:
        try:
            self.client.publish(topic, payload, retain=retain)
        except Exception as exc:  # pragma: no cover - depends on runtime broker
            LOGGER.error("Unable to publish MQTT message to %s: %s", topic, exc)

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: object,
        flags: dict[str, int],
        reason_code: int,
    ) -> None:
        del client, userdata, flags, reason_code
        try:
            self.client.subscribe("homeiq/+/+/set")
            self.client.subscribe("homeiq/devices/+/command")
            self.client.subscribe("homeiq/scenes/activate")
            self.client.subscribe("homeiq/simulation/control")
            if self.on_connected is not None:
                self.on_connected()
        except Exception as exc:  # pragma: no cover - depends on runtime broker
            LOGGER.error("Unable to subscribe to MQTT topics: %s", exc)

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: object,
        message: mqtt.MQTTMessage,
    ) -> None:
        del client, userdata

        try:
            payload = json.loads(message.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            LOGGER.error("Unable to decode MQTT payload on %s: %s", message.topic, exc)
            return

        try:
            if self._is_entity_set_topic(message.topic):
                self._handle_entity_command(message.topic, payload)
                return

            if message.topic.startswith("homeiq/devices/") and message.topic.endswith(
                "/command"
            ):
                self._handle_legacy_command(message.topic, payload)
                return

            if message.topic == "homeiq/scenes/activate":
                scene_id = str(payload["scene"])
                if self.on_scene_activate is not None:
                    self.on_scene_activate(scene_id)
                return

            if message.topic == "homeiq/simulation/control":
                self._handle_simulation_control(payload)
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.error("Unable to handle MQTT message on %s: %s", message.topic, exc)

    @staticmethod
    def _is_entity_set_topic(topic: str) -> bool:
        parts = topic.split("/")
        return len(parts) == 4 and parts[0] == "homeiq" and parts[3] == "set"

    def _handle_entity_command(self, topic: str, payload: dict[str, Any]) -> None:
        parts = topic.split("/")
        entity_id = f"{parts[1]}.{parts[2]}"
        state = str(payload.get("state", "off"))

        if self.on_device_command is not None:
            self.on_device_command(entity_id, state)

    def _handle_legacy_command(self, topic: str, payload: dict[str, Any]) -> None:
        device_id = topic.split("/")[2]
        raw_value = payload.get("value", payload.get("state"))

        if raw_value is None:
            raise KeyError("value")

        if device_id == "home_battery":
            device_id = "sensor.battery_soc"

        if self.on_device_command is not None:
            self.on_device_command(device_id, str(raw_value))

    def _handle_simulation_control(self, payload: dict[str, Any]) -> None:
        action = payload.get("action")
        simulator = self._simulator
        if simulator is None:
            return

        if action == "start":
            start = getattr(simulator, "start", None)
            if not callable(start):
                return

            speed = payload.get("speed")
            kwargs = {"speed": int(speed)} if speed is not None else {}

            if inspect.iscoroutinefunction(start):
                if self._loop is None or self._loop.is_closed():
                    raise RuntimeError("No event loop available for simulator start")
                asyncio.run_coroutine_threadsafe(start(**kwargs), self._loop)
            else:
                start(**kwargs)
        elif action == "stop":
            stop = getattr(simulator, "stop", None)
            if callable(stop):
                stop()
