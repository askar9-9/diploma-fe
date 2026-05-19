from __future__ import annotations

import numpy as np
import pytest

from app.anomaly_detector import AnomalyDetector
from app.constants import FEATURE_COLUMNS


def _make_trained_detector(n: int = 500) -> AnomalyDetector:
    detector = AnomalyDetector()
    X = detector._make_normal_data(n)
    detector.train(X)
    return detector


# ---------------------------------------------------------------------------
# test_train_and_detect_normal
# ---------------------------------------------------------------------------

def test_train_and_detect_normal():
    detector = _make_trained_detector(500)

    # A clearly normal daytime vector
    normal_fv = {
        "hour_of_day": 10,
        "weekday": 1,
        "motion_hall": 1,
        "motion_living": 1,
        "temperature": 22.0,
        "light_level": 90.0,
        "tv_on": 0,
        "minutes_idle": 5,
    }

    result = detector.detect(normal_fv)

    assert "anomaly" in result
    assert "score" in result
    assert "reason" in result
    assert result["anomaly"] is False


# ---------------------------------------------------------------------------
# test_detect_obvious_anomaly
# ---------------------------------------------------------------------------

def test_detect_obvious_anomaly():
    detector = _make_trained_detector(500)

    # Night hours, bright lights, no motion — suspicious
    night_fv = {
        "hour_of_day": 3,
        "weekday": 2,
        "motion_hall": 0,
        "motion_living": 0,
        "temperature": 22.0,
        "light_level": 90.0,  # high light at 3am with no motion
        "tv_on": 0,
        "minutes_idle": 5,
    }

    result = detector.detect(night_fv)

    # Either the model flags it as anomaly OR the rule-based reason mentions night/lights
    anomaly_flagged = result["anomaly"] is True
    reason_mentions_night = "night" in result["reason"].lower() or "light" in result["reason"].lower()

    assert anomaly_flagged or reason_mentions_night, (
        f"Expected anomaly flag or night/light mention in reason, got: {result}"
    )


# ---------------------------------------------------------------------------
# test_reason_high_temp_no_motion
# ---------------------------------------------------------------------------

def test_reason_high_temp_no_motion():
    detector = _make_trained_detector(500)

    fv = {
        "hour_of_day": 14,
        "weekday": 3,
        "motion_hall": 0,
        "motion_living": 0,
        "temperature": 25.0,   # > 24
        "light_level": 80.0,
        "tv_on": 0,
        "minutes_idle": 180,   # > 120
    }

    result = detector.detect(fv)
    assert "temperature" in result["reason"].lower(), (
        f"Expected 'temperature' in reason, got: {result['reason']!r}"
    )


# ---------------------------------------------------------------------------
# test_feature_columns_order
# ---------------------------------------------------------------------------

def test_feature_columns_order():
    """detect() must read features in FEATURE_COLUMNS order, not dict insertion order."""
    detector = _make_trained_detector(500)

    base_fv = {
        "hour_of_day": 10,
        "weekday": 1,
        "motion_hall": 1,
        "motion_living": 1,
        "temperature": 22.0,
        "light_level": 90.0,
        "tv_on": 0,
        "minutes_idle": 5,
    }

    # Reverse insertion order — result must be identical because detect() uses FEATURE_COLUMNS order
    reversed_fv = {col: base_fv[col] for col in reversed(FEATURE_COLUMNS)}

    result_base = detector.detect(base_fv)
    result_reversed = detector.detect(reversed_fv)

    assert result_base["anomaly"] == result_reversed["anomaly"]
    assert abs(result_base["score"] - result_reversed["score"]) < 1e-9
