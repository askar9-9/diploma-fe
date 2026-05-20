from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from db.models import DeviceState, MLHistory


client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    login = client.post(
        "/auth/login",
        json={"username": "admin", "password": "homeiq2026"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_feature_vector_route_uses_device_state_defaults_and_overrides():
    db = SessionLocal()
    try:
        db.merge(
            DeviceState(
                id="motion_hall",
                device_type="binary",
                value=1.0,
                updated_at=datetime.utcnow(),
            )
        )
        db.merge(
            DeviceState(
                id="tv_on",
                device_type="binary",
                value=1.0,
                updated_at=datetime.utcnow(),
            )
        )
        db.commit()
    finally:
        db.close()

    response = client.get("/ml/feature-vector", headers=_auth_headers())

    assert response.status_code == 200
    body = response.json()
    assert body["motion_hall"] == 1
    assert body["motion_living"] == 0
    assert body["temperature"] == 22.0
    assert body["tv_on"] == 1
    assert set(body.keys()) == {
        "hour_of_day",
        "weekday",
        "motion_hall",
        "motion_living",
        "temperature",
        "light_level",
        "tv_on",
        "minutes_idle",
    }


def test_manual_scene_activation_publishes_and_persists_history():
    published: list[str] = []
    messages: List[Dict[str, Any]] = []

    original_publish_scene = app.state.mqtt_handler.publish_scene
    original_broadcast = app.state.ws_manager.broadcast

    def fake_publish_scene(scene: str) -> None:
        published.append(scene)

    async def fake_broadcast(message: dict[str, Any]) -> None:
        messages.append(message)

    app.state.mqtt_handler.publish_scene = fake_publish_scene
    app.state.ws_manager.broadcast = fake_broadcast
    try:
        response = client.post(
            "/scenes/activate",
            json={"scene": "movie"},
            headers=_auth_headers(),
        )
    finally:
        app.state.mqtt_handler.publish_scene = original_publish_scene
        app.state.ws_manager.broadcast = original_broadcast

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "scene": "movie"}
    assert published == ["movie"]
    assert messages == [
        {
            "type": "scene_changed",
            "scene": "movie",
            "confidence": 1.0,
            "triggered_by": "manual",
        }
    ]

    db = SessionLocal()
    try:
        record = db.query(MLHistory).order_by(MLHistory.id.desc()).first()
        assert record is not None
        assert record.scenario == "movie"
        assert record.triggered_by == "manual"
        assert bool(record.applied) is True
    finally:
        db.close()


def test_devices_route_normalizes_simulator_registry(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            return None

        async def request(
            self,
            method: str,
            path: str,
            json: Optional[Dict[str, Any]] = None,
        ) -> httpx.Response:
            assert method == "GET"
            assert path == "/devices"
            return httpx.Response(
                200,
                json={
                    "motion_hall": {"type": "binary", "state": 1},
                    "temperature": {"type": "float", "state": 23.5},
                },
            )

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    response = client.get("/devices", headers=_auth_headers())
    body = response.json()

    assert response.status_code == 200
    assert len(body) == 2
    assert body[0]["id"] == "motion_hall"
    assert body[0]["name"] == "Motion Hall"
    assert body[0]["device_type"] == "binary"
    assert body[0]["state"] == 1.0
    assert body[0]["updated_at"]
    assert body[1]["id"] == "temperature"
    assert body[1]["name"] == "Temperature"
    assert body[1]["device_type"] == "float"
    assert body[1]["state"] == 23.5
    assert body[1]["updated_at"]


def test_devices_command_route_falls_back_to_state_endpoint(monkeypatch):
    calls: List[Tuple[str, str, Optional[Dict[str, Any]]]] = []

    class FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            return None

        async def request(
            self,
            method: str,
            path: str,
            json: Optional[Dict[str, Any]] = None,
        ) -> httpx.Response:
            calls.append((method, path, json))
            if path.endswith("/command"):
                return httpx.Response(404, json={"detail": "Not Found"})
            return httpx.Response(200, json={"type": "binary", "state": 1})

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    response = client.post(
        "/devices/ceiling_light/command",
        json={"value": 1},
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == {"type": "binary", "state": 1}
    assert calls == [
        ("POST", "/devices/ceiling_light/command", {"value": 1.0}),
        ("POST", "/devices/ceiling_light/state", {"value": 1.0}),
    ]
