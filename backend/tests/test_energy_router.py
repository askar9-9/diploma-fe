from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.routers.energy import get_ml_client


client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    login = client.post(
        "/auth/login",
        json={"username": "admin", "password": "homeiq2026"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_energy_forecast_proxies_ml_response(monkeypatch):
    class StubMLClient:
        async def energy_forecast(self, current_hour: int, weekday: int) -> dict:
            assert current_hour == 13
            assert weekday == 2
            return {
                "current_hour": current_hour,
                "weekday": weekday,
                "forecast": [],
                "total_kwh": 1.23,
                "peak_hour": 13,
                "peak_consumption_wh": 456.0,
                "recommendations": ["ok"],
            }

    class FrozenDatetime(datetime):
        @classmethod
        def utcnow(cls):
            return cls(2026, 5, 20, 13, 0, 0)

    import app.routers.energy as energy_module

    monkeypatch.setattr(energy_module, "datetime", FrozenDatetime)
    app.dependency_overrides[get_ml_client] = lambda: StubMLClient()
    try:
        response = client.get("/energy/forecast", headers=_auth_headers())
    finally:
        app.dependency_overrides.pop(get_ml_client, None)

    assert response.status_code == 200
    assert response.json()["total_kwh"] == 1.23
