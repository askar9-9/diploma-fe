# Spec: Scenario Clusterer

## Назначение

`ScenarioClusterer` группирует наборы feature vectors без разметки и возвращает результат кластеризации в формате, пригодном для последующего pattern suggestion.

## Контракт

```python
class ScenarioClusterer:
    def fit_predict(self, vectors: list[dict], n_clusters: int = 4) -> ClusterResult:
        # Использует KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        # Возвращает:
        # - n_clusters
        # - labels длиной len(vectors)
        # - centroids формы [n_clusters][8]
        # - inertia
```

## Acceptance Tests

### Given / When / Then
- Given: 20 валидных feature vectors
- When: вызывается `fit_predict(vectors, n_clusters=4)`
- Then: длина `labels` равна длине входного списка

- Given: 20 валидных feature vectors
- When: вызывается `fit_predict(vectors, n_clusters=4)`
- Then: число уникальных меток равно `4`

- Given: 20 валидных feature vectors
- When: вызывается `fit_predict(vectors, n_clusters=4)`
- Then: `centroids` содержит `4` центроида
