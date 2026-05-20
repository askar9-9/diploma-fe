# Spec: Frontend Auth + Layout

## Назначение
Собрать базовый frontend-скелет HomeIQ с JWT-авторизацией, защищёнными маршрутами и общим layout для семи разделов приложения (включая HEMS Dashboard).

## Контракт
- `authStore` хранит JWT в `localStorage` и предоставляет методы `getToken`, `setToken`, `clearToken`, `isAuthenticated`.
- `authApi.login(username, password)` отправляет `POST /auth/login` и возвращает `access_token`.
- `LoginPage` показывает форму логина, сохраняет токен после успешного входа и переводит пользователя на `/`.
- `PrivateRoute` пропускает только аутентифицированного пользователя, иначе редиректит на `/login`.
- `AppLayout` рисует sidebar и `Outlet` для контента. Использует светлую тему (bg-slate-50) с Home Assistant эстетикой. Иконки - `react-icons/md` (Material Design).
- `useWebSocket` подключается к `ws://.../ws?token=<jwt>` и отдаёт состояние соединения в layout.

## Acceptance Tests
### Given / When / Then
- Given: в `localStorage` нет токена
- When: пользователь открывает защищённый маршрут `/`
- Then: приложение редиректит на `/login`

- Given: пользователь ввёл неверные credentials
- When: отправлена форма логина
- Then: на странице появляется сообщение `Неверный логин или пароль`

- Given: backend вернул `access_token`
- When: форма логина успешно отправлена
- Then: токен сохраняется в `localStorage`, а пользователь попадает на `/`

- Given: в `localStorage` есть JWT
- When: layout монтируется
- Then: sidebar с разделами отображается, а WebSocket подключается с токеном в query string
