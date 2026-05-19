import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.suggester import PatternSuggester


BASE = {
    "hour_of_day": 20,
    "weekday": 3,
    "motion_hall": 0,
    "motion_living": 1,
    "temperature": 21.0,
    "light_level": 20.0,
    "tv_on": 1,
    "minutes_idle": 10,
}


def test_no_suggestion_few_occurrences():
    vectors = [BASE] * 3
    labels = [0] * 3
    result = PatternSuggester().suggest(vectors, labels, ["day", "night", "away", "movie"])
    assert result == []


def test_suggestion_enough_occurrences():
    vectors = [BASE] * 6
    labels = [0] * 6
    result = PatternSuggester().suggest(vectors, labels, [])
    assert len(result) == 1
    assert result[0].occurrence_count == 6


def test_suggestion_fields():
    vectors = [BASE] * 5
    labels = [0] * 5
    result = PatternSuggester().suggest(vectors, labels, [])
    assert hasattr(result[0], "cluster_id")
    assert hasattr(result[0], "median_values")
