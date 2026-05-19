import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.clusterer import ScenarioClusterer


VECTORS = [
    {
        "hour_of_day": h,
        "weekday": 1,
        "motion_hall": 0,
        "motion_living": 0,
        "temperature": 20.0,
        "light_level": 0.0,
        "tv_on": 0,
        "minutes_idle": 60,
    }
    for h in range(20)
]


def test_labels_length():
    r = ScenarioClusterer().fit_predict(VECTORS, n_clusters=4)
    assert len(r.labels) == len(VECTORS)


def test_unique_labels():
    r = ScenarioClusterer().fit_predict(VECTORS, n_clusters=4)
    assert len(set(r.labels)) == 4


def test_centroids_shape():
    r = ScenarioClusterer().fit_predict(VECTORS, n_clusters=4)
    assert len(r.centroids) == 4
