from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Callable

import paho.mqtt.client as mqtt


LOGGER = logging.getLogger(__name__)


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat()


class MQTTClient:
    def __init__(
        self,
        on_device_command: Callable[[str, float], None] | None = None,
        on_scene_activate: Callable[[str], None] | None = None,
        host: str | None = None,
        port: int | None = None,
    ) -> None:
        self.host = host or os.getenv("MQTT_HOST", "localhost")
        self.port = int(port or os.getenv("MQTT_PORT", "1883"))
        self.on_device_command = on_device_command
        self.on_scene_activate = on_scene_activate
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def connect(self) -> bool:
        try:
            self.client.connect(self.host, self.port)
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

    def publish_state(self, device_id: str, value: float) -> None:
        payload = json.dumps({"value": float(value), "timestamp": _timestamp()})
        self._publish(f"homeiq/devices/{device_id}/state", payload, retain=True)

    def publish_scene_confirmed(self, scene_id: str) -> None:
        payload = json.dumps({"scene": scene_id, "timestamp": _timestamp()})
        self._publish("homeiq/scenes/confirmed", payload, retain=False)

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
            self.client.subscribe("homeiq/devices/+/command")
            self.client.subscribe("homeiq/scenes/activate")
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
            if message.topic.startswith("homeiq/devices/") and message.topic.endswith(
                "/command"
            ):
                device_id = message.topic.split("/")[2]
                value = float(payload["value"])
                if self.on_device_command is not None:
                    self.on_device_command(device_id, value)
                return

            if message.topic == "homeiq/scenes/activate":
                scene_id = str(payload["scene"])
                if self.on_scene_activate is not None:
                    self.on_scene_activate(scene_id)
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.error("Unable to handle MQTT message on %s: %s", message.topic, exc)
