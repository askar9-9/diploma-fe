from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    login = client.post(
        "/auth/login",
        json={"username": "admin", "password": "homeiq2026"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_entities_returns_list():
    response = client.get("/entities", headers=_auth_headers())

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert any(item["entity_id"] == "switch.plug_tv_living" for item in body)


def test_post_entity_persists_and_delete_removes():
    entity_id = f"switch.plug_test_{uuid4().hex[:8]}"
    payload = {
        "entity_id": entity_id,
        "name": "Pytest Plug",
        "domain": "switch",
        "room": "kitchen",
    }
    headers = _auth_headers()

    create_response = client.post("/entities", json=payload, headers=headers)
    assert create_response.status_code == 201
    assert create_response.json()["room_ru"] == "Кухня"

    list_response = client.get("/entities", headers=headers)
    assert any(item["entity_id"] == entity_id for item in list_response.json())

    delete_response = client.delete(f"/entities/{entity_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": entity_id}


def test_entity_command_updates_state():
    headers = _auth_headers()

    response = client.post(
        "/entities/switch.plug_tv_living/command",
        json={"state": "on"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["state"] == "on"

    reset_response = client.post(
        "/entities/switch.plug_tv_living/command",
        json={"state": "off"},
        headers=headers,
    )
    assert reset_response.status_code == 200
