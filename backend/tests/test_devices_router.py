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


def test_get_devices_returns_list():
    response = client.get("/devices", headers=_auth_headers())

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_device_by_id():
    response = client.get("/devices/motion_hall", headers=_auth_headers())

    assert response.status_code == 200
    assert response.json()["id"] == "motion_hall"


def test_device_not_found():
    response = client.get("/devices/nonexistent", headers=_auth_headers())

    assert response.status_code == 404
