# Spec: Backend ML Coordination

## Назначение
Скоординировать реакцию Backend на изменение состояния устройств: обновить БД, собрать feature vector, обратиться к ML Service и при необходимости активировать сцену.

## Контракт
- `build_feature_vector(devices: dict, simulated_time: Optional[datetime] = None) -> dict`
  - Возвращает dict с ровно 8 признаками канонического Feature Schema
  - `hour_of_day`, `weekday` берутся из `simulated_time` или из `datetime.utcnow()`
  - `motion_hall`, `motion_living`, `tv_on` приводятся к `int`
  - `temperature`, `light_level` приводятся к `float`
  - `minutes_idle = 0`, если активен хотя бы один motion sensor, иначе `60`
- `MLClient.classify(feature_vector: dict) -> dict`
  - Делает `POST {ML_SERVICE_URL}/classify`
  - Возвращает `{"scenario","confidence","probabilities","alternative"}`
- `MLClient.cluster(vectors: list[dict], n_clusters: int = 4) -> dict`
  - Делает `POST {ML_SERVICE_URL}/cluster`
- `MLClient.suggest(vectors: list[dict], labels: list[int], known: list[str]) -> list`
  - Делает `POST {ML_SERVICE_URL}/suggest`
- `MQTT handler`
  - Подписывается на `homeiq/devices/+/state`, `homeiq/scenes/confirmed`, `homeiq/simulation/status`
  - При получении device state:
    - обновляет таблицы `devices` и `events`
    - вызывает `build_feature_vector`
    - вызывает `MLClient.classify`
    - сохраняет `FeatureVector`
    - при confidence выше `ML_CONFIDENCE_THRESHOLD` публикует `homeiq/scenes/activate`
    - рассылает обновление в WebSocket

## Acceptance Tests
### Given / When / Then
- Given: snapshot всех устройств
- When: backend строит feature vector
- Then: результат содержит 8 канонических признаков с корректными типами

- Given: simulated time `2024-01-01 14:00`
- When: backend строит feature vector
- Then: `hour_of_day == 14`

- Given: MQTT сообщение `homeiq/devices/motion_hall/state`
- When: backend обрабатывает payload
- Then: состояние устройства и событие сохраняются в БД, а frontend получает broadcast

- Given: ML классификатор вернул confidence выше порога
- When: backend завершает coordination cycle
- Then: публикуется команда активации сценария в `homeiq/scenes/activate`
