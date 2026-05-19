import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Optional

import paho.mqtt.client as mqtt

from backend.app.config import ML_CONFIDENCE_THRESHOLD, MQTT_HOST, MQTT_PORT
from backend.app.db import SessionLocal
from backend.app.feature_builder import build_feature_vector
from backend.app.ml_client import MLClient
from backend.app.websocket_manager import WebSocketManager
from backend.db.models import Device, Event, FeatureVector


logger = logging.getLogger(__name__)


class MQTTHandler:
    def __init__(self, ws_manager: WebSocketManager, ml_client: MLClient) -> None:
        self.ws_manager = ws_manager
        self.ml_client = ml_client
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def start(self) -> None:
        self.loop = asyncio.get_running_loop()
        self.client.reconnect_delay_set(min_delay=1, max_delay=10)
        self.client.connect_async(MQTT_HOST, MQTT_PORT, keepalive=60)
        self.client.loop_start()

    def stop(self) -> None:
        self.client.loop_stop()
        try:
            self.client.disconnect()
        except Exception:
            logger.exception("Failed to disconnect MQTT client cleanly")

    def publish_device_command(self, device_id: str, value: float) -> None:
        self.client.publish(
            f"homeiq/devices/{device_id}/command",
            json.dumps({"value": value}),
        )

    def publish_scene_activate(self, scenario_id: str) -> None:
        self.client.publish(
            "homeiq/scenes/activate",
            json.dumps({"scene": scenario_id}),
        )

    def publish_simulation_control(self, action: str, speed: Optional[int] = None) -> None:
        payload: dict[str, Any] = {"action": action}
        if speed is not None:
            payload["speed"] = speed
        self.client.publish("homeiq/simulation/control", json.dumps(payload))

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: dict, rc: int) -> None:
        if rc != 0:
            logger.warning("MQTT connect returned rc=%s", rc)
            return

        client.subscribe("homeiq/devices/+/state")
        client.subscribe("homeiq/scenes/confirmed")
        client.subscribe("homeiq/simulation/status")

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        if self.loop is None:
            return

        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            logger.warning("MQTT payload is not valid JSON for topic %s", msg.topic)
            return

        if msg.topic.endswith("/state"):
            future = asyncio.run_coroutine_threadsafe(
                self.handle_device_state(msg.topic, payload),
                self.loop,
            )
            future.add_done_callback(self._log_future_error)
        elif msg.topic == "homeiq/scenes/confirmed":
            future = asyncio.run_coroutine_threadsafe(
                self.ws_manager.broadcast({"type": "scene_confirmed", **payload}),
                self.loop,
            )
            future.add_done_callback(self._log_future_error)
        elif msg.topic == "homeiq/simulation/status":
            future = asyncio.run_coroutine_threadsafe(
                self.ws_manager.broadcast({"type": "simulation_status", **payload}),
                self.loop,
            )
            future.add_done_callback(self._log_future_error)

    def _log_future_error(self, future: asyncio.Future) -> None:
        try:
            future.result()
        except Exception:
            logger.exception("MQTT async task failed")

    async def handle_device_state(self, topic: str, payload: dict[str, Any]) -> None:
        device_id = topic.split("/")[2]
        new_state = float(payload.get("value", 0.0))
        session = SessionLocal()
        try:
            device = session.query(Device).filter(Device.id == device_id).first()
            if device is None:
                return

            now = datetime.utcnow()
            device.state = new_state
            device.updated_at = now
            session.add(
                Event(
                    device_id=device_id,
                    new_state=new_state,
                    attributes=json.dumps(payload),
                    created_at=now,
                )
            )
            session.commit()

            devices = session.query(Device).all()
            snapshot = {
                item.id: {
                    "state": item.state,
                    "device_type": item.device_type,
                }
                for item in devices
            }
            vector = build_feature_vector(snapshot)
            await self._coordinate_ml(session, vector)
            await self.ws_manager.broadcast(
                {
                    "type": "device_update",
                    "device_id": device_id,
                    "value": new_state,
                }
            )
        finally:
            session.close()

    async def _coordinate_ml(
        self,
        session,
        feature_vector: dict[str, Any],
    ) -> None:
        now = datetime.utcnow()
        predicted_scenario = None
        confidence = None
        decision_source = "classifier"

        try:
            result = await self.ml_client.classify(feature_vector)
            predicted_scenario = result.get("scenario")
            confidence = result.get("confidence")

            if confidence is not None and confidence >= ML_CONFIDENCE_THRESHOLD and predicted_scenario:
                self.publish_scene_activate(predicted_scenario)
            else:
                decision_source = "clusterer"
                try:
                    await self.ml_client.cluster([feature_vector])
                except Exception:
                    logger.exception("Cluster fallback failed")

            await self.ws_manager.broadcast(
                {
                    "type": "ml_decision",
                    "scenario": predicted_scenario,
                    "confidence": confidence,
                    "probabilities": result.get("probabilities"),
                    "alternative": result.get("alternative"),
                    "source": decision_source,
                }
            )
        except Exception:
            decision_source = "unavailable"
            logger.exception("ML classification failed")

        session.add(
            FeatureVector(
                hour_of_day=feature_vector["hour_of_day"],
                weekday=feature_vector["weekday"],
                motion_hall=feature_vector["motion_hall"],
                motion_living=feature_vector["motion_living"],
                temperature=feature_vector["temperature"],
                light_level=feature_vector["light_level"],
                tv_on=feature_vector["tv_on"],
                minutes_idle=feature_vector["minutes_idle"],
                predicted_scenario=predicted_scenario,
                confidence=confidence,
                decision_source=decision_source,
                created_at=now,
            )
        )
        session.commit()
