import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.classifier import ScenarioClassifier
from app.constants import FEATURE_COLUMNS


@pytest.fixture
def clf():
    c = ScenarioClassifier()
    X, y = c._make_synthetic_data()
    c.train(X, y)
    return c


FV = {
    "hour_of_day": 14,
    "weekday": 1,
    "motion_hall": 1,
    "motion_living": 0,
    "temperature": 22.0,
    "light_level": 80.0,
    "tv_on": 0,
    "minutes_idle": 5,
}


def test_predict_known_class(clf):
    assert clf.predict(FV).scenario in ["day", "night", "away", "movie"]


def test_confidence_range(clf):
    r = clf.predict(FV)
    assert 0.0 <= r.confidence <= 1.0


def test_probs_sum_to_one(clf):
    r = clf.predict(FV)
    assert abs(sum(r.probabilities.values()) - 1.0) < 1e-6


def test_alternative_differs(clf):
    r = clf.predict(FV)
    assert r.alternative != r.scenario


def test_accuracy_reasonable(clf):
    X, y = clf._make_synthetic_data()
    result = clf.train(X, y)
    assert result["accuracy"] > 0.7


def test_missing_feature_raises(clf):
    with pytest.raises((KeyError, ValueError)):
        clf.predict({"hour_of_day": 14})


def test_synthetic_data_respects_hour_rules():
    X, y = ScenarioClassifier()._make_synthetic_data()
    df = pd.DataFrame(np.asarray(X), columns=FEATURE_COLUMNS)
    df["scenario"] = y

    away_rows = df[df["hour_of_day"].between(0, 6)]
    assert not away_rows.empty
    assert (away_rows["scenario"] == "away").all()
    assert (away_rows["motion_hall"] == 0).all()
    assert (away_rows["motion_living"] == 0).all()
    assert (away_rows["light_level"] == 0).all()
    assert (away_rows["tv_on"] == 0).all()
    assert away_rows["temperature"].between(17, 19).all()
    assert away_rows["minutes_idle"].between(30, 480).all()

    day_rows = df[df["hour_of_day"].between(7, 17)]
    assert not day_rows.empty
    assert (day_rows["scenario"] == "day").all()
    assert (day_rows["motion_hall"] == 1).all()
    assert (day_rows["motion_living"] == 1).all()
    assert day_rows["light_level"].between(80, 100).all()
    assert (day_rows["tv_on"] == 0).all()
    assert day_rows["temperature"].between(21, 23).all()
    assert day_rows["minutes_idle"].between(0, 30).all()

    movie_rows = df[(df["hour_of_day"].between(18, 22)) & (df["scenario"] == "movie")]
    assert not movie_rows.empty
    assert (movie_rows["tv_on"] == 1).all()
    assert (movie_rows["light_level"] == 20).all()

    night_rows = df[df["hour_of_day"] == 23]
    assert not night_rows.empty
    assert (night_rows["scenario"] == "night").all()
    assert (night_rows["motion_hall"] == 0).all()
    assert (night_rows["motion_living"] == 0).all()
    assert (night_rows["light_level"] == 10).all()
    assert (night_rows["tv_on"] == 0).all()
    assert (night_rows["temperature"] == 20).all()
