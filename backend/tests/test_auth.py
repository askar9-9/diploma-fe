from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_login_success():
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "homeiq2026"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password():
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_protected_without_token():
    response = client.get("/devices")

    assert response.status_code == 401


def test_protected_with_token():
    login = client.post(
        "/auth/login",
        json={"username": "admin", "password": "homeiq2026"},
    )
    token = login.json()["access_token"]

    response = client.get(
        "/devices",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
