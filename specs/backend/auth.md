# Spec: Backend Auth

## Назначение
JWT-аутентификация для единственного администратора HomeIQ и защита REST/WebSocket интерфейсов Backend API.

## Контракт
- `POST /auth/login`
  - Request JSON: `{"username": str, "password": str}`
  - Success response: `{"access_token": str, "token_type": "bearer"}`
  - Error response: `401` при неверных credentials
- `create_access_token(data: dict) -> str`
  - Подписывает JWT через `python-jose`
  - Добавляет `exp` на 24 часа
- `verify_token(token: str) -> dict`
  - Возвращает payload валидного токена
  - Выбрасывает `HTTPException(status_code=401)` для невалидного токена
- `get_current_user(token: str = Depends(oauth2_scheme)) -> dict`
  - Извлекает payload текущего пользователя
- Все endpoints кроме `/auth/login` требуют `Authorization: Bearer <token>`

## Acceptance Tests
### Given / When / Then
- Given: корректные `admin` / `homeiq2026`
- When: клиент вызывает `POST /auth/login`
- Then: backend возвращает `200` и bearer token

- Given: неверный пароль
- When: клиент вызывает `POST /auth/login`
- Then: backend возвращает `401`

- Given: защищённый endpoint без токена
- When: клиент вызывает `GET /devices`
- Then: backend возвращает `401`

- Given: защищённый endpoint с валидным bearer token
- When: клиент вызывает `GET /devices`
- Then: backend возвращает `200`
