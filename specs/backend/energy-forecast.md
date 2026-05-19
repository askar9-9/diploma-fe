# Spec: Backend Energy Forecast Proxy

## Назначение
Backend должен отдавать frontend прогноз энергопотребления на 24 часа через защищенный endpoint, проксируя запрос в ML Service с текущими UTC-часом и днем недели.

## Контракт
- `GET /energy/forecast`
- Auth: требуется `Authorization: Bearer <token>`
- Источник данных: `MLClient.energy_forecast(current_hour: int, weekday: int) -> dict`
- Response: backend возвращает JSON ML Service без модификации структуры

## Acceptance Tests
### Given / When / Then
- Given: валидный JWT пользователя
- When: вызывается `GET /energy/forecast`
- Then: backend обращается к ML client с текущими `utc hour` и `weekday`

- Given: ответ от ML Service
- When: backend получает прогноз
- Then: endpoint возвращает этот прогноз с кодом `200`
