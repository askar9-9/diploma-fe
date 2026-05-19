# Spec: Pattern Suggester

## Назначение

`PatternSuggester` преобразует результаты кластеризации в предложения новых паттернов для ручного review. Предложение появляется только для кластеров, которые встретились не менее `MIN_OCCURRENCES`.

## Контракт

```python
MIN_OCCURRENCES = 5


class PatternSuggester:
    def suggest(
        self,
        vectors: list[dict],
        labels: list[int],
        known_scenarios: list[str],
    ) -> list[PatternSuggestion]:
        # Для каждого cluster_id c count >= MIN_OCCURRENCES:
        # - формирует PatternSuggestion
        # - occurrence_count = число элементов кластера
        # - time_window = агрегированное окно по часам
        # - weekdays = уникальные weekday
        # - median_values = медианы по признакам
```

## Acceptance Tests

### Given / When / Then
- Given: кластер с 3 элементами
- When: вызывается `suggest`
- Then: возвращается пустой список

- Given: кластер с 6 элементами
- When: вызывается `suggest`
- Then: возвращается один `PatternSuggestion` с `occurrence_count == 6`

- Given: кластер с 5 элементами
- When: вызывается `suggest`
- Then: объект результата содержит `cluster_id` и `median_values`
