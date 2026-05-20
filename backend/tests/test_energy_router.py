from datetime import datetime

from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.main import app
from db.models import EnergyReading


client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    login = client.post(
        "/auth/login",
        json={"username": "admin", "password": "homeiq2026"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_energy_history_returns_last_seven_days():
    db = SessionLocal()
    try:
        db.query(EnergyReading).delete()
        db.commit()

        for day in range(1, 9):
            db.add(
                EnergyReading(
                    date=f"2026-05-{day:02d}",
                    hour=12,
                    total_kwh=float(day),
                    created_at=datetime(2026, 5, day, 12, 0, 0),
                )
            )
        db.commit()
    finally:
        db.close()

    response = client.get("/energy/history", headers=_auth_headers())

    assert response.status_code == 200
    body = response.json()
    assert len(body["days"]) == 7
    assert body["days"][0]["date"] == "2026-05-02"
    assert body["days"][-1]["date"] == "2026-05-08"


def test_hems_forecast_proxies_ml_response(monkeypatch):
    async def stub_forecast() -> dict:
        return {
            "hours": list(range(24)),
            "load_forecast": [0.5] * 24,
            "solar_forecast": [1.0] * 24,
        }

    monkeypatch.setattr(app.state.ml_client, "hems_forecast", stub_forecast)

    response = client.get("/hems/forecast", headers=_auth_headers())

    assert response.status_code == 200
    assert response.json()["hours"] == list(range(24))


def test_hems_status_proxies_ml_response(monkeypatch):
    async def stub_status() -> dict:
        return {
            "current_hour": 13,
            "tariff_zone": "day",
            "tariff_price": 16.0,
            "optimizer_action": "idle",
            "recommendation": "ok",
        }

    monkeypatch.setattr(app.state.ml_client, "hems_status", stub_status)

    response = client.get("/hems/status", headers=_auth_headers())

    assert response.status_code == 200
    assert response.json()["tariff_zone"] == "day"
