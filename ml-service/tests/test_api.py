from datetime import datetime as real_datetime

from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_optimize_endpoint():
    payload = {
        "load_forecast": [1.0] * 24,
        "solar_forecast": [0.0] * 24,
        "battery_capacity": 10.0,
        "initial_soc": 0.0,
        "max_charge_rate": 5.0,
        "max_discharge_rate": 5.0,
        "prices": [1.0] * 24,
    }

    response = client.post("/hems/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "schedule" in data
    assert len(data["schedule"]) == 24
    assert "total_cost" in data


def test_forecast_endpoint():
    response = client.get("/hems/forecast")

    assert response.status_code == 200
    data = response.json()
    assert data["hours"] == list(range(24))
    assert len(data["load_forecast"]) == 24
    assert len(data["solar_forecast"]) == 24
    assert all(isinstance(value, float) for value in data["load_forecast"])
    assert all(isinstance(value, float) for value in data["solar_forecast"])


def test_status_endpoint_night_tariff(monkeypatch):
    class FakeDateTime:
        @classmethod
        def now(cls):
            return real_datetime(2026, 1, 10, 23, 0, 0)

    monkeypatch.setattr(main_module, "datetime", FakeDateTime)

    response = client.get("/hems/status")

    assert response.status_code == 200
    data = response.json()
    assert data["current_hour"] == 23
    assert data["tariff_zone"] == "night"
    assert data["tariff_price"] == 9.0
    assert data["optimizer_action"] == "charge"


def test_classify_endpoint():
    payload = {
        "features": {
            "hour_of_day": 14,
            "weekday": 1,
            "motion_hall": 1,
            "motion_living": 0,
            "temperature": 22.5,
            "light_level": 75.0,
            "tv_on": 0,
            "minutes_idle": 0,
        }
    }

    response = client.post("/classify", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["scenario"] == "day"
    assert data["alternative"] in {"night", "away", "movie"}
    assert data["confidence"] == data["probabilities"]["day"]
    assert set(data["probabilities"]) == {"day", "night", "away", "movie"}
    assert 0.0 <= data["confidence"] <= 1.0
    assert 0.99 <= sum(data["probabilities"].values()) <= 1.01


def test_classify_endpoint_clamps_out_of_range_features():
    payload = {
        "features": {
            "hour_of_day": 99,
            "weekday": -3,
            "motion_hall": 2,
            "motion_living": -1,
            "temperature": 35.0,
            "light_level": -10.0,
            "tv_on": 7,
            "minutes_idle": -15,
        }
    }

    response = client.post("/classify", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["scenario"] in {"day", "night", "away", "movie"}
    assert data["alternative"] in {"day", "night", "away", "movie"}
