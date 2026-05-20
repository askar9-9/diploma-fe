# Spec: Backend HA Entities API

## Назначение
Переход с `devices` (числовые состояния) на `entities` (HA-формат).
Персистентное хранение в SQLite. CRUD устройств. HA-стиль MQTT.
Удалить: classify, scenarios, patterns, ml_history endpoints.

## Стек
FastAPI :8000 + SQLAlchemy + SQLite (`data/homeiq.db`) + paho-mqtt + JWT

---

## SQLite схема (новые/изменённые таблицы)

### Таблица `entities`
```sql
CREATE TABLE entities (
    entity_id   TEXT PRIMARY KEY,          -- "binary_sensor.motion_hallway"
    name        TEXT NOT NULL,             -- "Xiaomi Mi Motion Sensor 2"
    model       TEXT NOT NULL DEFAULT '',  -- "RTCGQ02LM"
    domain      TEXT NOT NULL,             -- "binary_sensor"|"sensor"|"switch"|"light"|"climate"
    room        TEXT NOT NULL,             -- "hallway"|"living"|"kitchen"|"bedroom"|"bathroom"|"outdoor"|"utility"
    room_ru     TEXT NOT NULL,             -- "Прихожая"
    state       TEXT NOT NULL DEFAULT 'off',
    attributes  TEXT NOT NULL DEFAULT '{}', -- JSON строка
    doc_url     TEXT NOT NULL DEFAULT '',
    power_kw    REAL NOT NULL DEFAULT 0.0,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица `areas`
```sql
CREATE TABLE areas (
    id      TEXT PRIMARY KEY,   -- "hallway"
    name_ru TEXT NOT NULL       -- "Прихожая"
);
```

### Таблица `energy_readings`
```sql
CREATE TABLE energy_readings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    date       TEXT NOT NULL,   -- "2026-05-20"
    hour       INTEGER NOT NULL, -- 0-23
    total_kwh  REAL NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## Начальные данные (seed при старте если таблица пустая)

### Areas
```python
INITIAL_AREAS = [
    {"id": "hallway",  "name_ru": "Прихожая"},
    {"id": "living",   "name_ru": "Гостиная"},
    {"id": "kitchen",  "name_ru": "Кухня"},
    {"id": "bedroom",  "name_ru": "Спальня"},
    {"id": "bathroom", "name_ru": "Ванная"},
    {"id": "outdoor",  "name_ru": "Улица"},
    {"id": "utility",  "name_ru": "Котельная"},
]
```

### Entities (21 Xiaomi устройство)
```python
INITIAL_ENTITIES = [
    # Прихожая
    {"entity_id": "binary_sensor.motion_hallway", "name": "Xiaomi Mi Motion Sensor 2",
     "model": "RTCGQ02LM", "domain": "binary_sensor", "room": "hallway", "room_ru": "Прихожая",
     "state": "off", "attributes": '{"device_class":"motion"}',
     "doc_url": "https://www.mi.com/global/product/xiaomi-mi-motion-sensor-2", "power_kw": 0.0},
    {"entity_id": "binary_sensor.door_hallway", "name": "Aqara Door and Window Sensor",
     "model": "MCCGQ11LM", "domain": "binary_sensor", "room": "hallway", "room_ru": "Прихожая",
     "state": "off", "attributes": '{"device_class":"door"}',
     "doc_url": "https://www.aqara.com/us/door_and_window_sensor.html", "power_kw": 0.0},
    {"entity_id": "switch.plug_light_hallway", "name": "Xiaomi Mi Smart Plug 2",
     "model": "ZNCZ04LM", "domain": "switch", "room": "hallway", "room_ru": "Прихожая",
     "state": "off", "attributes": '{"device_class":"plug"}',
     "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2", "power_kw": 0.04},
    # Гостиная
    {"entity_id": "binary_sensor.motion_living", "name": "Xiaomi Mi Motion Sensor 2",
     "model": "RTCGQ02LM", "domain": "binary_sensor", "room": "living", "room_ru": "Гостиная",
     "state": "off", "attributes": '{"device_class":"motion"}',
     "doc_url": "https://www.mi.com/global/product/xiaomi-mi-motion-sensor-2", "power_kw": 0.0},
    {"entity_id": "light.ceiling_living", "name": "Yeelight Smart LED Bulb 1S",
     "model": "YLDP15YL", "domain": "light", "room": "living", "room_ru": "Гостиная",
     "state": "off", "attributes": '{"color_mode":"color_temp"}',
     "doc_url": "https://www.yeelight.com/en_US/product/lemon-color", "power_kw": 0.008},
    {"entity_id": "switch.plug_tv_living", "name": "Xiaomi Mi Smart Plug 2",
     "model": "ZNCZ04LM", "domain": "switch", "room": "living", "room_ru": "Гостиная",
     "state": "off", "attributes": '{"device_class":"plug"}',
     "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2", "power_kw": 0.15},
    {"entity_id": "sensor.light_level_living", "name": "Xiaomi Mi Light Detection Sensor",
     "model": "GZCGQ01LM", "domain": "sensor", "room": "living", "room_ru": "Гостиная",
     "state": "0.0", "attributes": '{"device_class":"illuminance","unit_of_measurement":"lx"}',
     "doc_url": "https://www.mi.com/global/", "power_kw": 0.0},
    # Кухня
    {"entity_id": "sensor.temperature_kitchen", "name": "Aqara Temperature and Humidity Sensor",
     "model": "WSDCGQ11LM", "domain": "sensor", "room": "kitchen", "room_ru": "Кухня",
     "state": "21.0", "attributes": '{"device_class":"temperature","unit_of_measurement":"°C"}',
     "doc_url": "https://www.aqara.com/us/temperature_humidity_sensor.html", "power_kw": 0.0},
    {"entity_id": "sensor.humidity_kitchen", "name": "Aqara Temperature and Humidity Sensor",
     "model": "WSDCGQ11LM", "domain": "sensor", "room": "kitchen", "room_ru": "Кухня",
     "state": "50.0", "attributes": '{"device_class":"humidity","unit_of_measurement":"%"}',
     "doc_url": "https://www.aqara.com/us/temperature_humidity_sensor.html", "power_kw": 0.0},
    {"entity_id": "switch.plug_kettle_kitchen", "name": "Xiaomi Mi Smart Plug 2",
     "model": "ZNCZ04LM", "domain": "switch", "room": "kitchen", "room_ru": "Кухня",
     "state": "off", "attributes": '{"device_class":"plug"}',
     "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2", "power_kw": 2.2},
    {"entity_id": "switch.plug_fridge_kitchen", "name": "Xiaomi Mi Smart Plug 2",
     "model": "ZNCZ04LM", "domain": "switch", "room": "kitchen", "room_ru": "Кухня",
     "state": "on", "attributes": '{"device_class":"plug"}',
     "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2", "power_kw": 0.15},
    {"entity_id": "binary_sensor.smoke_kitchen", "name": "Xiaomi Mi Smart Smoke Alarm",
     "model": "JTYJ-GD-01LM/BW", "domain": "binary_sensor", "room": "kitchen", "room_ru": "Кухня",
     "state": "off", "attributes": '{"device_class":"smoke"}',
     "doc_url": "https://www.mi.com/global/product/xiaomi-mi-smoke-alarm", "power_kw": 0.0},
    # Спальня
    {"entity_id": "binary_sensor.motion_bedroom", "name": "Xiaomi Mi Motion Sensor 2",
     "model": "RTCGQ02LM", "domain": "binary_sensor", "room": "bedroom", "room_ru": "Спальня",
     "state": "off", "attributes": '{"device_class":"motion"}',
     "doc_url": "https://www.mi.com/global/product/xiaomi-mi-motion-sensor-2", "power_kw": 0.0},
    {"entity_id": "light.bedside_bedroom", "name": "Yeelight LED Bedside Lamp D2",
     "model": "YLCT01YL", "domain": "light", "room": "bedroom", "room_ru": "Спальня",
     "state": "off", "attributes": '{"color_mode":"color_temp"}',
     "doc_url": "https://www.yeelight.com/en_US/product/lemon-color", "power_kw": 0.02},
    {"entity_id": "switch.plug_purifier_bedroom", "name": "Xiaomi Mi Air Purifier 3H",
     "model": "AC-M6-SC", "domain": "switch", "room": "bedroom", "room_ru": "Спальня",
     "state": "off", "attributes": '{"device_class":"plug"}',
     "doc_url": "https://www.mi.com/global/product/xiaomi-mi-air-purifier-3h", "power_kw": 0.038},
    # Ванная
    {"entity_id": "sensor.humidity_bathroom", "name": "Aqara Temperature and Humidity Sensor",
     "model": "WSDCGQ11LM", "domain": "sensor", "room": "bathroom", "room_ru": "Ванная",
     "state": "60.0", "attributes": '{"device_class":"humidity","unit_of_measurement":"%"}',
     "doc_url": "https://www.aqara.com/us/temperature_humidity_sensor.html", "power_kw": 0.0},
    {"entity_id": "switch.plug_boiler_bathroom", "name": "Xiaomi Mi Smart Plug 2",
     "model": "ZNCZ04LM", "domain": "switch", "room": "bathroom", "room_ru": "Ванная",
     "state": "off", "attributes": '{"device_class":"plug"}',
     "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2", "power_kw": 2.0},
    # Улица
    {"entity_id": "binary_sensor.motion_outdoor", "name": "Aqara Motion Sensor P1",
     "model": "MS-S02", "domain": "binary_sensor", "room": "outdoor", "room_ru": "Улица",
     "state": "off", "attributes": '{"device_class":"motion"}',
     "doc_url": "https://www.aqara.com/us/motion-sensor-p1.html", "power_kw": 0.0},
    {"entity_id": "light.outdoor_light", "name": "Xiaomi Mi Smart Outdoor Light",
     "model": "MUE4115GL", "domain": "light", "room": "outdoor", "room_ru": "Улица",
     "state": "off", "attributes": '{}',
     "doc_url": "https://www.mi.com/global/", "power_kw": 0.015},
    # Котельная
    {"entity_id": "climate.thermostat_main", "name": "Xiaomi Smart Home Hub 2",
     "model": "ZNDMWG03LM", "domain": "climate", "room": "utility", "room_ru": "Котельная",
     "state": "20.0", "attributes": '{"device_class":"temperature","unit_of_measurement":"°C","min":17,"max":25}',
     "doc_url": "https://www.mi.com/global/", "power_kw": 2.0},
    {"entity_id": "sensor.solar_panel", "name": "Xiaomi Solar Panel",
     "model": "BHR5164GL", "domain": "sensor", "room": "outdoor", "room_ru": "Улица",
     "state": "0.0", "attributes": '{"device_class":"power","unit_of_measurement":"kW"}',
     "doc_url": "https://www.mi.com/global/", "power_kw": 0.0},
    {"entity_id": "sensor.battery_soc", "name": "Xiaomi Smart Battery Pack",
     "model": "BHR5164GL", "domain": "sensor", "room": "utility", "room_ru": "Котельная",
     "state": "50.0", "attributes": '{"device_class":"battery","unit_of_measurement":"%"}',
     "doc_url": "https://www.mi.com/global/", "power_kw": 0.0},
]
```

---

## REST API Контракты

### Entities

#### GET /entities
Response: `list[EntitySchema]`
```python
class EntitySchema(BaseModel):
    entity_id: str
    name: str
    model: str
    domain: str
    room: str
    room_ru: str
    state: str
    attributes: dict
    doc_url: str
    power_kw: float
    updated_at: str
```

#### POST /entities (требует JWT)
Request:
```python
class CreateEntityRequest(BaseModel):
    entity_id: str
    name: str
    model: str = ""
    domain: str
    room: str
    doc_url: str = ""
    power_kw: float = 0.0
```
- Проверить уникальность entity_id → 409 Conflict если уже существует
- room_ru вычислить из справочника (hallway→Прихожая и т.д.)
- Записать в SQLite, вернуть созданную сущность

#### DELETE /entities/{entity_id} (требует JWT)
- Удалить из SQLite, вернуть `{"deleted": entity_id}`

#### POST /entities/{entity_id}/command (требует JWT)
Request: `{"state": "on"}`
- Обновить state в SQLite
- Опубликовать MQTT: topic=`homeiq/{domain}/{name}/set`, payload=`{"state": "on"}`
- Разослать WebSocket: `{"type": "state_changed", "entity_id": ..., "state": ..., "attributes": ...}`
- Вернуть `{"status": "ok", "entity_id": ..., "state": ...}`

### Areas

#### GET /areas
Response:
```python
class AreaSchema(BaseModel):
    id: str
    name_ru: str
    entities: list[str]  # entity_ids из таблицы entities
```

### Energy

#### GET /energy/history
Response:
```python
class EnergyHistoryResponse(BaseModel):
    days: list[dict]  # [{"date": "2026-05-14", "total_kwh": 12.5}, ...]
```
- Последние 7 дней из таблицы `energy_readings`
- Агрегация: SUM(total_kwh) GROUP BY date

#### POST /energy/reading (внутренний, вызывается из mqtt_handler)
Записывает текущее потребление (sum power_kw активных switch+light) с временной меткой.

---

## MQTT (HA-стиль)

### Топики подписки (Simulator → Backend)
```
homeiq/{domain}/{entity_name}/state
```
Payload: `{"state": "on"|"off"|"21.5", "attributes": {...}}`

При получении:
1. Обновить `entities.state` в SQLite
2. Разослать WebSocket `{"type": "state_changed", entity_id, state, attributes}`
3. Если switch/light и state изменился → записать energy_reading

### Топики публикации (Backend → Simulator)
```
homeiq/{domain}/{entity_name}/set
```
Payload: `{"state": "on"|"off"|"21.5"}`

Где `entity_name` — часть после точки в entity_id (`motion_hallway` из `binary_sensor.motion_hallway`)

---

## Что удалить из бэкенда

- `backend/app/routers/scenarios.py`
- `backend/app/routers/anomaly.py`
- `backend/app/routers/ml_history.py`
- `backend/app/routers/simulation.py` (или сохранить заглушку)
- `backend/app/feature_builder.py` (если не нужен для энергии)
- Все вызовы `/classify` в `ml_client.py`
- Убрать роуты из `main.py`

## Что оставить

- `backend/app/routers/auth.py` — без изменений
- `backend/app/routers/websocket.py` — обновить формат сообщений
- `backend/app/routers/energy.py` — обновить под новую схему
- `backend/app/routers/areas.py` — переписать под новую схему
- Прокси вызовы к ML Service: `/hems/forecast`, `/hems/status`

---

## Acceptance Tests

### B1: Seed данные
- Given: пустая БД
- When: старт FastAPI
- Then: 22 entities в таблице, 7 areas

### B2: GET /entities
- When: GET /entities (с JWT)
- Then: 200, список 22 объектов с полями entity_id, name, model, domain, room, state

### B3: POST /entities
- When: POST /entities `{"entity_id": "switch.plug_test", "name": "Test", "domain": "switch", "room": "kitchen"}`
- Then: 201, создан объект, GET /entities возвращает 23

### B4: Command с MQTT
- When: POST /entities/switch.plug_tv_living/command `{"state": "on"}`
- Then: state в БД = "on", MQTT публикация в `homeiq/switch/plug_tv_living/set`

### B5: MQTT → state update
- When: приходит MQTT `homeiq/binary_sensor/motion_hallway/state` с `{"state": "on"}`
- Then: entities.state обновлён, WebSocket разослал state_changed

### B6: GET /energy/history
- When: есть записи за 7 дней
- Then: 200, массив 7 объектов с date + total_kwh
