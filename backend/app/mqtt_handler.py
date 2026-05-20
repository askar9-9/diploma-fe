from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Union

import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session

from app.config import ML_CONFIDENCE_THRESHOLD, MQTT_HOST, MQTT_PORT
from app.db import SessionLocal
from app.energy_service import add_energy_reading
from app.ml_features import DEVICE_METADATA, MOTION_DEVICE_IDS, build_feature_vector
from app.websocket_manager import WebSocketManager
from db.models import DeviceState, Entity, MLHistory


logger = logging.getLogger(__name__)


def entity_name_from_entity_id(entity_id: str) -> str:
    return entity_id.split(".", 1)[1] if "." in entity_id else entity_id


class MQTTHandler:
    def __init__(self, ws_manager: WebSocketManager, app_state: Any) -> None:
        self.ws_manager = ws_manager
        self.app_state = app_state
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

    def publish_entity_command(self, domain: str, entity_name: str, state: str) -> None:
        self.client.publish(
            f"homeiq/{domain}/{entity_name}/set",
            json.dumps({"state": state}),
        )

    def publish_scene(self, scene: str) -> None:
        self.client.publish(
            "homeiq/scenes/activate",
            json.dumps({"scene": scene}),
        )

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: dict[str, Any], rc: int) -> None:
        if rc != 0:
            logger.warning("MQTT connect returned rc=%s", rc)
            return

        client.subscribe("homeiq/+/+/state")
        client.subscribe("homeiq/scenes/confirmed")

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        if self.loop is None:
            return

        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            logger.warning("MQTT payload is not valid JSON for topic %s", msg.topic)
            return

        if msg.topic == "homeiq/scenes/confirmed":
            coroutine = self.handle_scene_confirmation(payload)
        else:
            coroutine = self.handle_state_message(msg.topic, payload)

        future = asyncio.run_coroutine_threadsafe(
            coroutine,
            self.loop,
        )
        future.add_done_callback(self._log_future_error)

    def _log_future_error(self, future: asyncio.Future[Any]) -> None:
        try:
            future.result()
        except Exception:
            logger.exception("MQTT async task failed")

    async def handle_entity_state(self, topic: str, payload: dict[str, Any]) -> None:
        parts = topic.split("/")
        domain, entity_name = parts[1], parts[2]
        entity_id = f"{domain}.{entity_name}"
        new_state = str(payload.get("state", ""))
        attributes_payload = payload.get("attributes")
        new_attributes = attributes_payload if isinstance(attributes_payload, dict) else None

        session = SessionLocal()
        try:
            entity = session.get(Entity, entity_id)
            if entity is None:
                logger.info("Ignoring MQTT update for unknown entity %s", entity_id)
                return

            state_changed = entity.state != new_state
            attributes_changed = new_attributes is not None and entity.attributes != new_attributes

            if not state_changed and not attributes_changed:
                return

            entity.state = new_state
            if new_attributes is not None:
                entity.attributes = new_attributes
            entity.updated_at = datetime.utcnow()

            if state_changed and entity.domain in {"switch", "light"}:
                add_energy_reading(session, entity.updated_at)

            session.commit()
            session.refresh(entity)

            await self.ws_manager.broadcast(
                {
                    "type": "state_changed",
                    "entity_id": entity.entity_id,
                    "state": entity.state,
                    "attributes": entity.attributes or {},
                }
            )
            await self._run_ml_classification(session)
        finally:
            session.close()

    async def handle_state_message(self, topic: str, payload: dict[str, Any]) -> None:
        parts = topic.split("/")
        if len(parts) != 4 or parts[0] != "homeiq" or parts[3] != "state":
            logger.warning("Unexpected MQTT topic: %s", topic)
            return

        if parts[1] == "devices":
            await self.handle_device_state(parts[2], payload)
            return

        await self.handle_entity_state(topic, payload)

    async def handle_device_state(self, device_id: str, payload: dict[str, Any]) -> None:
        raw_value = payload.get("value", payload.get("state", 0.0))
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            logger.warning("Invalid device value for %s: %r", device_id, raw_value)
            return

        timestamp_raw = payload.get("timestamp")
        updated_at = datetime.utcnow()
        if isinstance(timestamp_raw, str):
            try:
                updated_at = datetime.fromisoformat(timestamp_raw)
            except ValueError:
                logger.warning("Invalid device timestamp for %s: %s", device_id, timestamp_raw)

        if device_id in MOTION_DEVICE_IDS and value > 0.0:
            self.app_state.last_motion_at = updated_at

        session = SessionLocal()
        try:
            device_type = DEVICE_METADATA.get(device_id, {}).get("device_type", "float")
            device_state = session.get(DeviceState, device_id)
            if device_state is None:
                device_state = DeviceState(
                    id=device_id,
                    device_type=device_type,
                    value=value,
                    updated_at=updated_at,
                )
                session.add(device_state)
            else:
                device_state.device_type = device_type
                device_state.value = value
                device_state.updated_at = updated_at

            session.commit()
            await self._run_ml_classification(session)
        finally:
            session.close()

    async def handle_scene_confirmation(self, payload: dict[str, Any]) -> None:
        scene = str(payload.get("scene", "")).strip()
        if not scene:
            return

        self.app_state.current_scene = scene

    def _build_feature_vector(self, session: Session) -> Dict[str, Union[int, float]]:
        return build_feature_vector(
            session,
            last_motion_at=getattr(self.app_state, "last_motion_at", None),
        )

    async def _run_ml_classification(self, session: Session) -> None:
        feature_vector = self._build_feature_vector(session)

        try:
            result = await self.app_state.ml_client.classify(feature_vector)
        except Exception:
            logger.warning("ML classify call failed", exc_info=True)
            return

        scenario = str(result.get("scenario", ""))
        confidence = float(result.get("confidence", 0.0))
        probabilities = result.get("probabilities", {})
        if not isinstance(probabilities, dict):
            probabilities = {}

        applied = confidence >= ML_CONFIDENCE_THRESHOLD
        ml_record = MLHistory(
            scenario=scenario,
            confidence=confidence,
            probabilities=probabilities,
            applied=applied,
            feature_vector=feature_vector,
            triggered_by="auto",
        )
        session.add(ml_record)
        session.commit()
        session.refresh(ml_record)

        should_activate_scene = applied and bool(scenario) and scenario != self.app_state.current_scene
        if applied:
            self.app_state.current_scene = scenario or self.app_state.current_scene
            self.app_state.last_confidence = confidence
            self.app_state.last_decision_at = ml_record.created_at.isoformat()

        if should_activate_scene:
            self.publish_scene(scenario)

        await self.ws_manager.broadcast(
            {
                "type": "ml_decision",
                "scenario": scenario,
                "confidence": confidence,
                "probabilities": probabilities,
                "applied": applied,
                "feature_vector": feature_vector,
            }
        )
        if should_activate_scene:
            await self.ws_manager.broadcast(
                {
                    "type": "scene_changed",
                    "scene": scenario,
                    "confidence": confidence,
                    "triggered_by": "auto",
                }
            )
