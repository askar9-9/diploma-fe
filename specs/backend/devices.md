# Spec: Backend Devices API

## Назначение
Предоставить frontend доступ к реестру устройств HomeIQ и к ручной отправке команд в Device Simulator через MQTT.

## Контракт
- `GET /devices`
  - Требует JWT
  - Возвращает список всех устройств из таблицы `devices`
- `GET /devices/{id}`
  - Требует JWT
  - Возвращает устройство по `id`
  - Возвращает `404`, если устройство не найдено
- `POST /devices/{id}/command`
  - Требует JWT
  - Request JSON: `{"value": float}`
  - Публикует MQTT-сообщение в `homeiq/devices/{id}/command`
  - Возвращает подтверждение публикации

## Acceptance Tests
### Given / When / Then
- Given: валидный JWT и инициализированная БД
- When: клиент вызывает `GET /devices`
- Then: backend возвращает список из seed-устройств

- Given: валидный JWT и существующее устройство `motion_hall`
- When: клиент вызывает `GET /devices/motion_hall`
- Then: backend возвращает объект устройства с `id="motion_hall"`

- Given: валидный JWT и несуществующее устройство
- When: клиент вызывает `GET /devices/nonexistent`
- Then: backend возвращает `404`

- Given: валидный JWT и команда на устройство
- When: клиент вызывает `POST /devices/{id}/command`
- Then: backend публикует MQTT-команду в корректный топик и возвращает `200`
