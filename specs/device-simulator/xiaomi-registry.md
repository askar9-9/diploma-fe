# Spec: Device Simulator — Xiaomi Registry + HA MQTT

## Назначение
Расширить Device Simulator с 8 хардкодных устройств до 21 Xiaomi-устройства.
Перейти на HA-стиль MQTT топиков и payload.
Поддержать динамическое добавление устройств через backend API.

## Стек
FastAPI :8002 + paho-mqtt + SQLite (читает из backend SQLite)

---

## Новый реестр устройств

Заменить `INITIAL_DEVICES` в `app/devices.py` на `XIAOMI_DEVICES`:

```python
XIAOMI_DEVICES: dict[str, dict] = {
    # Прихожая
    "binary_sensor.motion_hallway": {
        "name": "Xiaomi Mi Motion Sensor 2", "model": "RTCGQ02LM",
        "domain": "binary_sensor", "room": "hallway",
        "state": "off", "power_kw": 0.0,
        "attributes": {"device_class": "motion"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-mi-motion-sensor-2",
        "sim": {"type": "binary", "on_prob": 0.1}
    },
    "binary_sensor.door_hallway": {
        "name": "Aqara Door and Window Sensor", "model": "MCCGQ11LM",
        "domain": "binary_sensor", "room": "hallway",
        "state": "off", "power_kw": 0.0,
        "attributes": {"device_class": "door"},
        "doc_url": "https://www.aqara.com/us/door_and_window_sensor.html",
        "sim": {"type": "binary", "on_prob": 0.05}
    },
    "switch.plug_light_hallway": {
        "name": "Xiaomi Mi Smart Plug 2", "model": "ZNCZ04LM",
        "domain": "switch", "room": "hallway",
        "state": "off", "power_kw": 0.04,
        "attributes": {"device_class": "plug"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2",
        "sim": {"type": "binary", "on_prob": 0.3}
    },
    # Гостиная
    "binary_sensor.motion_living": {
        "name": "Xiaomi Mi Motion Sensor 2", "model": "RTCGQ02LM",
        "domain": "binary_sensor", "room": "living",
        "state": "off", "power_kw": 0.0,
        "attributes": {"device_class": "motion"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-mi-motion-sensor-2",
        "sim": {"type": "binary", "on_prob": 0.2}
    },
    "light.ceiling_living": {
        "name": "Yeelight Smart LED Bulb 1S", "model": "YLDP15YL",
        "domain": "light", "room": "living",
        "state": "off", "power_kw": 0.008,
        "attributes": {"color_mode": "color_temp"},
        "doc_url": "https://www.yeelight.com/en_US/product/lemon-color",
        "sim": {"type": "binary", "on_prob": 0.4}
    },
    "switch.plug_tv_living": {
        "name": "Xiaomi Mi Smart Plug 2", "model": "ZNCZ04LM",
        "domain": "switch", "room": "living",
        "state": "off", "power_kw": 0.15,
        "attributes": {"device_class": "plug"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2",
        "sim": {"type": "binary", "on_prob": 0.25}
    },
    "sensor.light_level_living": {
        "name": "Xiaomi Mi Light Detection Sensor", "model": "GZCGQ01LM",
        "domain": "sensor", "room": "living",
        "state": "0.0", "power_kw": 0.0,
        "attributes": {"device_class": "illuminance", "unit_of_measurement": "lx"},
        "doc_url": "https://www.mi.com/global/",
        "sim": {"type": "float", "min": 0.0, "max": 1000.0, "step": 50.0}
    },
    # Кухня
    "sensor.temperature_kitchen": {
        "name": "Aqara Temperature and Humidity Sensor", "model": "WSDCGQ11LM",
        "domain": "sensor", "room": "kitchen",
        "state": "21.0", "power_kw": 0.0,
        "attributes": {"device_class": "temperature", "unit_of_measurement": "°C"},
        "doc_url": "https://www.aqara.com/us/temperature_humidity_sensor.html",
        "sim": {"type": "float", "min": 18.0, "max": 28.0, "step": 0.5}
    },
    "sensor.humidity_kitchen": {
        "name": "Aqara Temperature and Humidity Sensor", "model": "WSDCGQ11LM",
        "domain": "sensor", "room": "kitchen",
        "state": "50.0", "power_kw": 0.0,
        "attributes": {"device_class": "humidity", "unit_of_measurement": "%"},
        "doc_url": "https://www.aqara.com/us/temperature_humidity_sensor.html",
        "sim": {"type": "float", "min": 30.0, "max": 80.0, "step": 2.0}
    },
    "switch.plug_kettle_kitchen": {
        "name": "Xiaomi Mi Smart Plug 2", "model": "ZNCZ04LM",
        "domain": "switch", "room": "kitchen",
        "state": "off", "power_kw": 2.2,
        "attributes": {"device_class": "plug"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2",
        "sim": {"type": "binary", "on_prob": 0.1}
    },
    "switch.plug_fridge_kitchen": {
        "name": "Xiaomi Mi Smart Plug 2", "model": "ZNCZ04LM",
        "domain": "switch", "room": "kitchen",
        "state": "on", "power_kw": 0.15,
        "attributes": {"device_class": "plug"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2",
        "sim": {"type": "always_on"}
    },
    "binary_sensor.smoke_kitchen": {
        "name": "Xiaomi Mi Smart Smoke Alarm", "model": "JTYJ-GD-01LM/BW",
        "domain": "binary_sensor", "room": "kitchen",
        "state": "off", "power_kw": 0.0,
        "attributes": {"device_class": "smoke"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-mi-smoke-alarm",
        "sim": {"type": "binary", "on_prob": 0.001}
    },
    # Спальня
    "binary_sensor.motion_bedroom": {
        "name": "Xiaomi Mi Motion Sensor 2", "model": "RTCGQ02LM",
        "domain": "binary_sensor", "room": "bedroom",
        "state": "off", "power_kw": 0.0,
        "attributes": {"device_class": "motion"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-mi-motion-sensor-2",
        "sim": {"type": "binary", "on_prob": 0.15}
    },
    "light.bedside_bedroom": {
        "name": "Yeelight LED Bedside Lamp D2", "model": "YLCT01YL",
        "domain": "light", "room": "bedroom",
        "state": "off", "power_kw": 0.02,
        "attributes": {"color_mode": "color_temp"},
        "doc_url": "https://www.yeelight.com/en_US/product/lemon-color",
        "sim": {"type": "binary", "on_prob": 0.2}
    },
    "switch.plug_purifier_bedroom": {
        "name": "Xiaomi Mi Air Purifier 3H", "model": "AC-M6-SC",
        "domain": "switch", "room": "bedroom",
        "state": "off", "power_kw": 0.038,
        "attributes": {"device_class": "plug"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-mi-air-purifier-3h",
        "sim": {"type": "binary", "on_prob": 0.5}
    },
    # Ванная
    "sensor.humidity_bathroom": {
        "name": "Aqara Temperature and Humidity Sensor", "model": "WSDCGQ11LM",
        "domain": "sensor", "room": "bathroom",
        "state": "60.0", "power_kw": 0.0,
        "attributes": {"device_class": "humidity", "unit_of_measurement": "%"},
        "doc_url": "https://www.aqara.com/us/temperature_humidity_sensor.html",
        "sim": {"type": "float", "min": 40.0, "max": 90.0, "step": 3.0}
    },
    "switch.plug_boiler_bathroom": {
        "name": "Xiaomi Mi Smart Plug 2", "model": "ZNCZ04LM",
        "domain": "switch", "room": "bathroom",
        "state": "off", "power_kw": 2.0,
        "attributes": {"device_class": "plug"},
        "doc_url": "https://www.mi.com/global/product/xiaomi-smart-plug2",
        "sim": {"type": "binary", "on_prob": 0.15}
    },
    # Улица
    "binary_sensor.motion_outdoor": {
        "name": "Aqara Motion Sensor P1", "model": "MS-S02",
        "domain": "binary_sensor", "room": "outdoor",
        "state": "off", "power_kw": 0.0,
        "attributes": {"device_class": "motion"},
        "doc_url": "https://www.aqara.com/us/motion-sensor-p1.html",
        "sim": {"type": "binary", "on_prob": 0.05}
    },
    "light.outdoor_light": {
        "name": "Xiaomi Mi Smart Outdoor Light", "model": "MUE4115GL",
        "domain": "light", "room": "outdoor",
        "state": "off", "power_kw": 0.015,
        "attributes": {},
        "doc_url": "https://www.mi.com/global/",
        "sim": {"type": "binary", "on_prob": 0.3}
    },
    # Котельная
    "climate.thermostat_main": {
        "name": "Xiaomi Smart Home Hub 2", "model": "ZNDMWG03LM",
        "domain": "climate", "room": "utility",
        "state": "20.0", "power_kw": 2.0,
        "attributes": {"device_class": "temperature", "unit_of_measurement": "°C", "min": 17, "max": 25},
        "doc_url": "https://www.mi.com/global/",
        "sim": {"type": "float", "min": 17.0, "max": 25.0, "step": 0.5}
    },
    "sensor.solar_panel": {
        "name": "Xiaomi Solar Panel", "model": "BHR5164GL",
        "domain": "sensor", "room": "outdoor",
        "state": "0.0", "power_kw": 0.0,
        "attributes": {"device_class": "power", "unit_of_measurement": "kW"},
        "doc_url": "https://www.mi.com/global/",
        "sim": {"type": "solar"}
    },
    "sensor.battery_soc": {
        "name": "Xiaomi Smart Battery Pack", "model": "BHR5164GL",
        "domain": "sensor", "room": "utility",
        "state": "50.0", "power_kw": 0.0,
        "attributes": {"device_class": "battery", "unit_of_measurement": "%"},
        "doc_url": "https://www.mi.com/global/",
        "sim": {"type": "float", "min": 10.0, "max": 100.0, "step": 1.0}
    },
}
```

---

## MQTT топики (HA-стиль)

### Публикация состояния (Simulator → Backend)
```
Topic:   homeiq/{domain}/{entity_name}/state
Payload: {"state": "on"|"off"|"21.5", "attributes": {...}}
```
Где `entity_name` — часть после точки (`motion_hallway` из `binary_sensor.motion_hallway`)

### Подписка на команды (Backend → Simulator)
```
Topic:   homeiq/{domain}/{entity_name}/set
Payload: {"state": "on"|"off"|"21.5"}
```

---

## DeviceRegistry (обновлённый класс)

```python
class DeviceRegistry:
    def __init__(self):
        self._devices: dict[str, dict] = {}
        self._load_initial()

    def _load_initial(self):
        for entity_id, data in XIAOMI_DEVICES.items():
            self._devices[entity_id] = dict(data)

    def get_all(self) -> dict:
        return {k: dict(v) for k, v in self._devices.items()}

    def get(self, entity_id: str) -> dict:
        if entity_id not in self._devices:
            raise KeyError(entity_id)
        return dict(self._devices[entity_id])

    def set_state(self, entity_id: str, state: str) -> str:
        if entity_id not in self._devices:
            raise KeyError(entity_id)
        self._devices[entity_id]["state"] = state
        return state

    def add_device(self, entity_id: str, data: dict) -> None:
        """Добавить устройство динамически (из backend API при старте)"""
        self._devices[entity_id] = data

    def reset(self) -> None:
        self._load_initial()
```

---

## MQTT клиент (обновлённый)

Методы:
```python
def publish_entity_state(entity_id: str, state: str, attributes: dict) -> None:
    domain, name = entity_id.split(".", 1)
    topic = f"homeiq/{domain}/{name}/state"
    payload = json.dumps({"state": state, "attributes": attributes})
    client.publish(topic, payload)

def subscribe_entity_commands() -> None:
    # Подписаться на homeiq/+/+/set
    client.subscribe("homeiq/+/+/set")

def on_command_message(client, userdata, message) -> None:
    # Парсить topic: homeiq/{domain}/{name}/set
    parts = message.topic.split("/")  # ["homeiq", domain, name, "set"]
    entity_id = f"{parts[1]}.{parts[2]}"
    payload = json.loads(message.payload)
    state = payload.get("state", "off")
    registry.set_state(entity_id, str(state))
```

---

## Симуляция (периодическая публикация)

Каждые 5 секунд для каждого устройства:
- `sim.type == "binary"` → случайно переключать с вероятностью `on_prob`
- `sim.type == "float"` → случайно двигать на ±step в пределах [min, max]
- `sim.type == "always_on"` → state всегда "on"
- `sim.type == "solar"` → синусоидальная кривая по часу суток (пик ~13:00, ночью 0)

Публиковать MQTT при каждом изменении состояния.

---

## REST API (device-simulator)

### GET /devices (совместимость, deprecated)
Вернуть список устройств в старом формате (для обратной совместимости на период перехода).

### GET /entities
Вернуть все устройства в новом HA-формате.

### POST /entities/{entity_id}/command
Установить состояние устройства вручную (тест/отладка).

### GET /simulation/status
Текущее состояние симуляции.

### POST /simulation/start | /simulation/stop

---

## Acceptance Tests

### D1: Реестр загружен
- Given: старт Simulator
- When: GET /entities
- Then: 21 устройство, все с entity_id в формате `domain.name`

### D2: MQTT публикация HA-формат
- When: симулятор публикует состояние
- Then: topic = `homeiq/binary_sensor/motion_hallway/state`, payload = `{"state": "off", "attributes": {"device_class": "motion"}}`

### D3: Команда через MQTT
- When: публикуется `homeiq/switch/plug_tv_living/set` с `{"state": "on"}`
- Then: registry.get("switch.plug_tv_living")["state"] == "on"

### D4: Симуляция
- When: симуляция запущена 10 секунд
- Then: хотя бы одно устройство изменило state (кроме always_on)

### D5: Динамическое добавление
- When: вызван add_device("switch.plug_new", {...})
- Then: GET /entities возвращает 22 устройства
