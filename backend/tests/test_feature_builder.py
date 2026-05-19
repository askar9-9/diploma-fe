from datetime import datetime

from app.feature_builder import build_feature_vector


def test_all_8_features_present():
    devices = {
        "motion_hall": {"state": 0.0},
        "motion_living": {"state": 1.0},
        "temperature": {"state": 22.5},
        "light_level": {"state": 55.0},
        "tv_on": {"state": 0.0},
    }

    vector = build_feature_vector(devices)

    assert set(vector.keys()) == {
        "hour_of_day",
        "weekday",
        "motion_hall",
        "motion_living",
        "temperature",
        "light_level",
        "tv_on",
        "minutes_idle",
    }


def test_hour_from_simulated_time():
    devices = {
        "motion_hall": {"state": 0.0},
        "motion_living": {"state": 0.0},
        "temperature": {"state": 22.5},
        "light_level": {"state": 55.0},
        "tv_on": {"state": 0.0},
    }

    vector = build_feature_vector(devices, simulated_time=datetime(2024, 1, 1, 14, 0))

    assert vector["hour_of_day"] == 14


def test_motion_binary():
    devices = {
        "motion_hall": {"state": 1.0},
        "motion_living": {"state": 0.0},
        "temperature": {"state": 22.5},
        "light_level": {"state": 55.0},
        "tv_on": {"state": 0.0},
    }

    vector = build_feature_vector(devices)

    assert vector["motion_hall"] == 1


def test_no_simulated_time_uses_real():
    devices = {
        "motion_hall": {"state": 0.0},
        "motion_living": {"state": 0.0},
        "temperature": {"state": 22.5},
        "light_level": {"state": 55.0},
        "tv_on": {"state": 0.0},
    }

    vector = build_feature_vector(devices)

    assert 0 <= vector["hour_of_day"] <= 23
