# Spec: HEMS Coordination (Backend <-> ML Client)

## Назначение

Определяет периодическое взаимодействие Backend с ML-сервисом (через `ml_client.py`) для оптимизации энергопотребления (HEMS). 
Ранее система отправляла фичи на каждое изменение состояния (`feature_vectors`). Теперь Backend будет вызывать ручку ML по расписанию, чтобы запросить оптимальные команды заряда батареи и управлять состоянием системы.

## Архитектура взаимодействия

1. **Периодический вызов:** Backend содержит планировщик (например, `APScheduler` или `asyncio.sleep` таску в фоне), который вызывает `ml_client.optimize_energy()` каждые N минут (например, 15 минут).
2. **Получение данных:** 
   - `ml_client.optimize_energy()` обращается к эндпоинту ML-сервиса: `POST /hems/optimize`.
   - Тело запроса включает текущее состояние энергосистемы: `battery_soc`, `solar_generation`, `ev_soc`, `house_consumption`. (Состояния берутся из БД или реестра устройств).
3. **Ответ ML-сервиса:** 
   - ML-сервис возвращает предписание по управлению, например: `{"home_battery_cmd": -2.0, "ev_charger_cmd": 0.0}` (мощность заряда в кВт).
4. **Применение команд:** 
   - `mqtt_handler.py` или отдельный сервис рассылает полученные команды в MQTT брокер:
     - `homeiq/device/home_battery/command`
     - `homeiq/device/ev_charger/command`
5. **Сохранение в БД:**
   - Каждое рассчитанное/обновленное состояние энергии записывается в таблицу `energy_states` для истории.

## Acceptance Tests

### Тест 1: Вызов `/hems/optimize`
- Given: Backend имеет расписание для вызова `optimize_energy()`.
- When: Срабатывает таймер расписания.
- Then: Вызывается `ml_client` с текущими значениями устройств `home_battery`, `solar_panel`, `ev_charger` и `grid_power/house_consumption`. 

### Тест 2: Применение команд
- Given: `ml_client.optimize_energy()` вернул `{"home_battery_cmd": 5.0}`.
- When: Команда обрабатывается бэкендом.
- Then: В MQTT топик `homeiq/device/home_battery/command` отправляется payload `{"state": 5.0}` (или аналогичный по контракту).
