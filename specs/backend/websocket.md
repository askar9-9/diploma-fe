# Spec: Backend WebSocket Broadcast

## Назначение
Поддерживать realtime-канал между Backend и Frontend для доставки обновлений устройств, сцен, статуса симуляции и ML-решений.

## Контракт
- `GET /ws?token=<jwt>`
  - Принимает WebSocket-соединение только при валидном JWT
- `WebSocketManager`
  - `connect(ws: WebSocket)` добавляет клиента в `active` и принимает соединение
  - `disconnect(ws: WebSocket)` удаляет клиента из `active`
  - `broadcast(message: dict)` сериализует сообщение через `json.dumps` и рассылает всем активным клиентам
- MQTT и REST-слой используют один shared manager для broadcast событий

## Acceptance Tests
### Given / When / Then
- Given: валидный JWT
- When: frontend открывает `GET /ws`
- Then: backend принимает WebSocket-соединение

- Given: активные WebSocket-клиенты
- When: backend вызывает `broadcast({"type": "device_update", ...})`
- Then: все активные клиенты получают одинаковый JSON payload

- Given: WebSocket отключился
- When: backend вызывает `disconnect`
- Then: клиент удаляется из списка `active`
