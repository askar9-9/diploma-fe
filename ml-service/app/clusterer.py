from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans

from app.constants import FEATURE_COLUMNS
from app.schemas import ClusterResult, FeatureVector


class ScenarioClusterer:
    def fit_predict(self, vectors: list[dict], n_clusters: int = 4) -> ClusterResult:
        if len(vectors) < n_clusters:
            raise ValueError("Number of vectors must be at least n_clusters")

        matrix = np.array(
            [
                [getattr(FeatureVector(**vector), column) for column in FEATURE_COLUMNS]
                for vector in vectors
            ],
            dtype=float,
        )

        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = model.fit_predict(matrix)

        return ClusterResult(
            n_clusters=n_clusters,
            labels=labels.astype(int).tolist(),
            centroids=model.cluster_centers_.astype(float).tolist(),
            inertia=float(model.inertia_),
        )
