# Spec: Scene Execution

## Назначение

Логика исполнения предустановленных сцен умного дома. Принимает текущий реестр устройств и идентификатор сцены, возвращает обновлённый реестр. Чистая функция — без MQTT side effects.

## Контракт

```python
# Константы
SCENES: dict[str, dict]  # 4 предустановленные сцены и их целевые состояния

# Функции (чистые)
def get_all_scenes() -> dict
    # Возвращает копию словаря всех сцен.

def apply_scene(devices: dict, scene_id: str) -> dict
    # Применяет сцену к реестру устройств.
    # Возвращает обновлённый dict устройств.
    # Raises: ValueError если scene_id не существует в SCENES.
```

## Сцены (целевые состояния устройств)

```python
SCENES = {
    "day":   {"ceiling_light": 1, "bedside_light": 0, "light_level": 100.0, "thermostat": 22.0, "tv_on": 0},
    "night": {"ceiling_light": 0, "bedside_light": 1, "light_level": 10.0,  "thermostat": 20.0, "tv_on": 0},
    "away":  {"ceiling_light": 0, "bedside_light": 0, "light_level": 0.0,   "thermostat": 17.0, "tv_on": 0},
    "movie": {"ceiling_light": 0, "bedside_light": 0, "light_level": 20.0,  "thermostat": 22.0, "tv_on": 1},
}
```

## Acceptance Tests

### test_activate_day
- Given: реестр устройств в начальном состоянии
- When: apply_scene(devices, "day")
- Then: ceiling_light.state == 1, tv_on.state == 0, light_level.state == 100.0
- Then: thermostat.state == 22.0, bedside_light.state == 0

### test_activate_night
- Given: реестр устройств в начальном состоянии
- When: apply_scene(devices, "night")
- Then: bedside_light.state == 1, light_level.state == 10.0
- Then: ceiling_light.state == 0, thermostat.state == 20.0

### test_activate_away
- Given: реестр устройств в начальном состоянии
- When: apply_scene(devices, "away")
- Then: ceiling_light.state == 0, bedside_light.state == 0
- Then: light_level.state == 0.0, thermostat.state == 17.0, tv_on.state == 0

### test_activate_movie
- Given: реестр устройств в начальном состоянии
- When: apply_scene(devices, "movie")
- Then: tv_on.state == 1, light_level.state == 20.0
- Then: ceiling_light.state == 0, thermostat.state == 22.0

### test_invalid_scene
- Given: реестр устройств
- When: apply_scene(devices, "unknown_scene")
- Then: ValueError поднимается
