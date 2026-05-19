from __future__ import annotations

import numpy as np

from app.constants import FEATURE_COLUMNS
from app.schemas import PatternSuggestion, FeatureVector

MIN_OCCURRENCES = 5


class PatternSuggester:
    def suggest(
        self,
        vectors: list[dict],
        labels: list[int],
        known_scenarios: list[str],
    ) -> list[PatternSuggestion]:
        if len(vectors) != len(labels):
            raise ValueError("vectors and labels must have the same length")

        _ = known_scenarios
        normalized_vectors = [FeatureVector(**vector).model_dump() for vector in vectors]
        suggestions: list[PatternSuggestion] = []

        for cluster_id in sorted(set(labels)):
            cluster_vectors = [
                vector
                for vector, label in zip(normalized_vectors, labels)
                if label == cluster_id
            ]
            occurrence_count = len(cluster_vectors)

            if occurrence_count < MIN_OCCURRENCES:
                continue

            median_values = {
                column: float(np.median([vector[column] for vector in cluster_vectors]))
                for column in FEATURE_COLUMNS
            }
            median_hour = int(round(median_values["hour_of_day"]))
            time_window = {
                "hour_start": max(0, median_hour - 1),
                "hour_end": min(23, median_hour + 1),
            }
            weekdays = sorted({int(vector["weekday"]) for vector in cluster_vectors})

            suggestions.append(
                PatternSuggestion(
                    cluster_id=int(cluster_id),
                    occurrence_count=occurrence_count,
                    time_window=time_window,
                    weekdays=weekdays,
                    median_values=median_values,
                )
            )

        return suggestions
