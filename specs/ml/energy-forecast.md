# Spec: ML Energy Forecast

## Назначение
Сервис ML должен строить прогноз энергопотребления дома на ближайшие 24 часа, используя существующий классификатор сценариев и фиксированные мощности устройств.

## Контракт
- `POST /energy/forecast`
- Request:
  - `current_hour: int` в диапазоне `0..23`
  - `weekday: int` в диапазоне `0..6`
- Response:
  - `current_hour: int`
  - `weekday: int`
  - `forecast: list[EnergyHourForecast]` из 24 точек
  - `total_kwh: float`
  - `peak_hour: int`
  - `peak_consumption_wh: float`
  - `recommendations: list[str]`

- Внутренний модуль:
  - `calculate_consumption_wh(scene: str) -> float`
  - `predict_scene_for_hour(hour: int, weekday: int, classifier) -> tuple[str, float]`
  - `EnergyForecaster.forecast_24h(classifier, current_hour: int, weekday: int) -> list[dict]`
  - `EnergyForecaster.daily_total_kwh(forecast: list[dict]) -> float`
  - `EnergyForecaster.peak_hour(forecast: list[dict]) -> dict`
  - `EnergyForecaster.recommendations(forecast: list[dict]) -> list[str]`

## Acceptance Tests
### Given / When / Then
- Given: сцена `day`
- When: вызывается `calculate_consumption_wh("day")`
- Then: возвращается сумма `ceiling_light + thermostat`

- Given: стартовый час прогноза
- When: вызывается `forecast_24h(...)`
- Then: возвращается ровно 24 часовые точки с корректным переходом через `23 -> 0`

- Given: классификатор недоступен или падает
- When: вызывается предсказание сцены для часа
- Then: применяется fallback-логика по правилам времени суток

- Given: сформированный 24-часовой прогноз
- When: считаются итоги и рекомендации
- Then: сервис возвращает суммарное потребление, пиковый час и хотя бы одну рекомендацию
