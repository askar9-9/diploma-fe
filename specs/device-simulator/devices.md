# Spec: Device Registry

## Назначение

Реестр виртуальных IoT-устройств умного дома. Хранит состояния 8 устройств в памяти (dict). Предоставляет чистые функции для чтения и обновления состояний — без side effects (MQTT вызывается снаружи).

## Контракт

```python
# Константы
INITIAL_DEVICES: dict[str, dict]  # начальные состояния 8 устройств

# Функции (чистые — без MQTT side effects)
def get_all_devices(devices: dict) -> dict
    # Возвращает копию словаря всех устройств с их состояниями.

def get_device(devices: dict, device_id: str) -> dict
    # Возвращает состояние одного устройства.
    # Raises: KeyError если device_id не существует.

def update_device_state(devices: dict, device_id: str, value) -> dict
    # Устанавливает новое значение state для устройства.
    # Возвращает обновлённый словарь устройств.
    # Raises: KeyError если device_id не существует.
    # Raises: ValueError если тип значения не соответствует типу устройства.
```

## Устройства (начальные состояния)

```python
INITIAL_DEVICES = {
    "motion_hall":   {"type": "binary", "state": 0},
    "motion_living": {"type": "binary", "state": 0},
    "temperature":   {"type": "float",  "state": 20.0},
    "light_level":   {"type": "float",  "state": 0.0},
    "ceiling_light": {"type": "binary", "state": 0},
    "bedside_light": {"type": "binary", "state": 0},
    "thermostat":    {"type": "float",  "state": 20.0},
    "tv_on":         {"type": "binary", "state": 0},
}
```

## Acceptance Tests

### test_initial_state
- Given: реестр проинициализирован через INITIAL_DEVICES
- When: читаем все устройства
- Then: все 8 устройств присутствуют с правильными начальными состояниями

### test_update_binary
- Given: motion_hall имеет state=0
- When: update_device_state(devices, "motion_hall", 1)
- Then: motion_hall.state == 1
- When: update_device_state(devices, "motion_hall", 0)
- Then: motion_hall.state == 0

### test_update_float
- Given: temperature имеет state=20.0
- When: update_device_state(devices, "temperature", 25.5)
- Then: temperature.state == 25.5

### test_invalid_device
- Given: реестр проинициализирован
- When: update_device_state(devices, "nonexistent", 1)
- Then: KeyError поднимается

### test_get_all_devices
- Given: реестр проинициализирован
- When: get_all_devices(devices)
- Then: возвращается словарь с ровно 8 ключами, соответствующими INITIAL_DEVICES
