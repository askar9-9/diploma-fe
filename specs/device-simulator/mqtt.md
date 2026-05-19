# Spec: MQTT Client

## Назначение

MQTT-клиент Device Simulator. Публикует состояния устройств и подтверждения сцен. Подписывается на команды изменения состояний и активации сцен. При старте публикует все начальные состояния с retain=True. Если MQTT недоступен — приложение стартует, логирует ошибку.

## Конфигурация (ENV)

```
MQTT_HOST=localhost  (default)
MQTT_PORT=1883       (default)
```

## Топики (строго по CLAUDE.md)

### Публикует:

| Топик | Payload | Флаги |
|---|---|---|
| `homeiq/devices/{device_id}/state` | `{"value": <state>, "timestamp": "<iso>"}` | retain=True, QoS=0 |
| `homeiq/scenes/confirmed` | `{"scene": "<scene_id>", "timestamp": "<iso>"}` | retain=False, QoS=0 |

### Подписывается:

| Топик | Действие |
|---|---|
| `homeiq/devices/{device_id}/command` | Устанавливает state, публикует `homeiq/devices/{device_id}/state` |
| `homeiq/scenes/activate` | Исполняет сцену, публикует state каждого устройства + `homeiq/scenes/confirmed` |

## Контракт

```python
class MQTTClient:
    def __init__(self, host: str, port: int, devices: dict, on_device_update: Callable, on_scene_activate: Callable)
        # host, port — из ENV
        # devices — ссылка на общий реестр состояний
        # on_device_update(device_id, value) — callback при получении команды
        # on_scene_activate(scene_id) — callback при получении сцены

    def connect(self) -> bool
        # Подключается к брокеру.
        # Возвращает True при успехе, False при ошибке.
        # При ошибке — логирует, не бросает исключение.

    def publish_device_state(self, device_id: str, value) -> None
        # Публикует в homeiq/devices/{device_id}/state с retain=True.
        # Payload: {"value": value, "timestamp": "<iso>"}

    def publish_scene_confirmed(self, scene_id: str) -> None
        # Публикует в homeiq/scenes/confirmed.
        # Payload: {"scene": scene_id, "timestamp": "<iso>"}

    def publish_all_states(self, devices: dict) -> None
        # Публикует состояния всех устройств с retain=True.
        # Вызывается при старте приложения.

    def disconnect(self) -> None
        # Корректно отключается от брокера.
```

## Acceptance Tests (с mock MQTT)

### test_publish_device_state_topic
- Given: MQTTClient с mock paho.mqtt.client
- When: publish_device_state("ceiling_light", 1)
- Then: mock.publish вызван с топиком "homeiq/devices/ceiling_light/state"
- Then: payload содержит {"value": 1} и поле "timestamp"
- Then: retain=True

### test_publish_scene_confirmed_topic
- Given: MQTTClient с mock paho.mqtt.client
- When: publish_scene_confirmed("day")
- Then: mock.publish вызван с топиком "homeiq/scenes/confirmed"
- Then: payload содержит {"scene": "day"} и поле "timestamp"

### test_on_command_message
- Given: MQTTClient с mock callback on_device_update
- When: приходит MQTT-сообщение в топик "homeiq/devices/ceiling_light/command" с payload {"value": 1}
- Then: on_device_update("ceiling_light", 1) вызван ровно один раз

### test_on_scene_activate_message
- Given: MQTTClient с mock callback on_scene_activate
- When: приходит MQTT-сообщение в топик "homeiq/scenes/activate" с payload {"scene": "day"}
- Then: on_scene_activate("day") вызван ровно один раз

### test_connect_failure_no_exception
- Given: MQTT-брокер недоступен (mock raises exception)
- When: mqtt_client.connect()
- Then: исключение не пробрасывается наружу
- Then: возвращает False
- Then: ошибка залогирована
