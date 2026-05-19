import pytest

from app.energy_forecaster import (
    DEVICE_POWER_WATTS,
    SCENE_DEVICE_STATES,
    EnergyForecaster,
    calculate_consumption_wh,
)


def test_consumption_day_scene():
    """day: ceiling_light(60) + thermostat(1500) = 1560Вт"""
    result = calculate_consumption_wh("day")
    assert result == 60.0 + 1500.0


def test_consumption_away_scene():
    """away: только 30% термостата = 450Вт"""
    result = calculate_consumption_wh("away")
    assert result == 1500.0 * 0.3


def test_consumption_movie_scene():
    """movie: thermostat(1500) + tv_on(120) = 1620Вт"""
    result = calculate_consumption_wh("movie")
    assert result == 1500.0 + 120.0


def test_consumption_night_scene():
    """night: bedside_light(10) + 70% thermostat(1050) = 1060Вт"""
    result = calculate_consumption_wh("night")
    assert result == 10.0 + 1500.0 * 0.7


def test_forecast_returns_24_points():
    forecaster = EnergyForecaster()

    class MockClassifier:
        def predict(self, fv):
            class R:
                scenario = "day"
                confidence = 0.9

            return R()

    result = forecaster.forecast_24h(MockClassifier(), current_hour=0, weekday=1)
    assert len(result) == 24


def test_forecast_hours_wrap_around():
    """Часы должны быть 0-23, не выходить за границу"""
    forecaster = EnergyForecaster()

    class MockClassifier:
        def predict(self, fv):
            class R:
                scenario = "day"
                confidence = 0.9

            return R()

    result = forecaster.forecast_24h(MockClassifier(), current_hour=22, weekday=1)
    hours = [p["hour"] for p in result]
    assert all(0 <= h <= 23 for h in hours)
    assert hours[0] == 22
    assert hours[2] == 0


def test_daily_total_positive():
    forecaster = EnergyForecaster()
    fake = [{"consumption_kwh": 1.5} for _ in range(24)]
    assert forecaster.daily_total_kwh(fake) == pytest.approx(36.0)


def test_peak_hour_finds_max():
    forecaster = EnergyForecaster()
    fake = [{"hour": i, "consumption_wh": i * 100} for i in range(24)]
    peak = forecaster.peak_hour(fake)
    assert peak["hour"] == 23


def test_recommendations_not_empty():
    forecaster = EnergyForecaster()
    fake = [
        {"consumption_kwh": 1.0, "scenario": "day", "consumption_wh": 1000}
        for _ in range(24)
    ]
    tips = forecaster.recommendations(fake)
    assert len(tips) >= 1
    assert all(isinstance(t, str) for t in tips)


def test_device_maps_cover_supported_scenes():
    assert "thermostat" in DEVICE_POWER_WATTS
    assert set(SCENE_DEVICE_STATES) == {"day", "night", "away", "movie"}
