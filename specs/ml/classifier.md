# Spec: Scenario Classifier

## Назначение

`ScenarioClassifier` обучает и применяет классификацию сценариев HomeIQ по неизменной Feature Schema из 8 признаков. Если внешней модели нет, классификатор должен уметь обучиться на синтетических данных, согласованных с целевыми классами `day`, `night`, `away`, `movie`.

## Контракт

```python
FEATURE_COLUMNS = [
    "hour_of_day",
    "weekday",
    "motion_hall",
    "motion_living",
    "temperature",
    "light_level",
    "tv_on",
    "minutes_idle",
]

TARGET_CLASSES = ["day", "night", "away", "movie"]


class ScenarioClassifier:
    def _make_synthetic_data(self) -> tuple[np.ndarray, list[str]]:
        # Генерирует 2000 строк с random_state=42.
        # Правила:
        # - hour 0-6   -> away: motion=0, light=0, tv=0, temp=17-19
        # - hour 7-17  -> day: motion=1, light=80-100, tv=0, temp=21-23
        # - hour 18-22 -> movie(60%) или day(40%)
        #   * movie: tv=1, light=20
        # - hour 23    -> night: motion=0, light=10, tv=0, temp=20
        # - minutes_idle: 0-30 при motion, 30-480 при away
        # - weekday: 0-6 random

    def train(self, X: np.ndarray, y: list[str]) -> dict:
        # Использует RandomForestClassifier(n_estimators=100, random_state=42)
        # Возвращает {"accuracy": float, "classes": list[str]}

    def predict(self, fv: dict) -> ClassificationResult:
        # Требует все 8 ключей Feature Schema
        # При отсутствии любого признака поднимает ValueError

    def save(self, path: str) -> None:
        # Сохраняет модель через joblib

    def load(self, path: str) -> None:
        # Загружает модель через joblib
```

## Acceptance Tests

### Given / When / Then
- Given: обученный классификатор и валидный `FeatureVector`
- When: вызывается `predict`
- Then: `scenario` входит в `["day", "night", "away", "movie"]`

- Given: обученный классификатор и валидный `FeatureVector`
- When: вызывается `predict`
- Then: `confidence` находится в диапазоне `0.0..1.0`

- Given: обученный классификатор и валидный `FeatureVector`
- When: вызывается `predict`
- Then: сумма значений `probabilities` равна `1.0` с точностью `1e-6`

- Given: обученный классификатор и валидный `FeatureVector`
- When: вызывается `predict`
- Then: `alternative != scenario`

- Given: синтетические данные из `_make_synthetic_data`
- When: вызывается `train`
- Then: `accuracy > 0.7`

- Given: неполный feature vector
- When: вызывается `predict`
- Then: поднимается `ValueError`

- Given: строки синтетического набора
- When: они фильтруются по диапазонам часов
- Then: значения motion/light/tv/temp/minutes_idle соответствуют правилам генерации
