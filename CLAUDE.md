# HomeIQ — Smart Home ML System

Дипломный проект: система управления умным домом на основе машинного обучения.

## Структура репозитория (Mono-repo)

```
homeiq/                     ← diploma-fe/ is the root
├── frontend/               ← React 18 + TypeScript + Vite + Tailwind CSS
├── backend/                ← FastAPI :8000
├── ml-service/             ← FastAPI + scikit-learn :8001
├── device-simulator/       ← FastAPI + paho-mqtt :8002
├── infra/                  ← mosquitto config
├── specs/                  ← spec-файлы по SDD (ОБЯЗАТЕЛЬНЫ до реализации)
│   ├── frontend/
│   ├── backend/
│   ├── ml/
│   ├── device-simulator/
│   └── infra/
├── docker-compose.yml
└── CLAUDE.md
```

## Архитектура

```
Frontend (Nginx :80)
    ↕ REST / WebSocket
Backend API (FastAPI :8000)
    ↕ HTTP REST          ↕ MQTT (paho)
ML Service (:8001)    Mosquitto (:1883)
                          ↕ MQTT
                      Device Simulator (:8002)
                          ↕ SQLite (data/homeiq.db)
```

**Правило:** Backend — единственная точка входа для Frontend. ML Service не знает о MQTT и БД. Device Simulator не знает о ML.

## Feature Schema (каноническая — единая для всей системы)

| Признак         | Тип   | Диапазон  | Источник                               |
|-----------------|-------|-----------|----------------------------------------|
| `hour_of_day`   | int   | 0–23      | Виртуальное время Simulator / sysclock |
| `weekday`       | int   | 0–6       | Sysclock или виртуальная дата          |
| `motion_hall`   | int   | 0/1       | Device: `motion_hall`                  |
| `motion_living` | int   | 0/1       | Device: `motion_living`                |
| `temperature`   | float | 15.0–30.0 | Device: `temperature`                  |
| `light_level`   | float | 0.0–100.0 | Device: `light_level`                  |
| `tv_on`         | int   | 0/1       | Device: `tv_on`                        |
| `minutes_idle`  | int   | 0–480     | Backend: время с последнего движения   |

**Целевые классы:** `day`, `night`, `away`, `movie` (расширяются через Pattern Review).

## Устройства (Device Simulator)

| ID               | Тип    | Диапазон    |
|------------------|--------|-------------|
| `motion_hall`    | binary | 0/1         |
| `motion_living`  | binary | 0/1         |
| `temperature`    | float  | 15.0–30.0°C |
| `light_level`    | float  | 0–100       |
| `ceiling_light`  | binary | 0/1         |
| `bedside_light`  | binary | 0/1         |
| `thermostat`     | float  | 17–25°C     |
| `tv_on`          | binary | 0/1         |

## Предустановленные сцены

| Сцена   | ceiling_light | bedside_light | light_level | thermostat | tv_on |
|---------|---------------|---------------|-------------|------------|-------|
| `day`   | 1             | 0             | 100         | 22         | 0     |
| `night` | 0             | 1             | 10          | 20         | 0     |
| `away`  | 0             | 0             | 0           | 17         | 0     |
| `movie` | 0             | 0             | 20          | 22         | 1     |

## ML Dataset

Используем **CASAS Smart Home Dataset** (WSU). Скрипт маппинга: `ml-service/scripts/prepare_casas.py`. Маппинг → Feature Schema → обучение Random Forest. Модели хранятся в `ml-service/data/models/` через joblib с версионированием по timestamp.

## Методология: Spec-Driven Development + строгий TDD

**Правило:** реализация без spec-файла запрещена.

### Цикл разработки

```
ADR → Spec-файл (specs/<layer>/<task>.md)
  → Failing test (RED)
    → Минимальная реализация (GREEN)
      → Refactor (REFACTOR)
```

### Структура spec-файла

```markdown
# Spec: <название>

## Назначение
<что делает этот модуль>

## Контракт
<сигнатуры функций / endpoint-описания>

## Acceptance Tests
### Given / When / Then
- Given: <предусловие>
- When: <действие>
- Then: <ожидаемый результат>
```

## Тестовый стек

| Слой             | Инструменты                          |
|------------------|--------------------------------------|
| Backend (Python) | pytest + pytest-asyncio + httpx      |
| ML Service       | pytest + numpy                       |
| Device Simulator | pytest + pytest-asyncio + httpx      |
| Frontend (TS)    | Vitest + React Testing Library + MSW |

## MVP — Приоритеты (дедлайн 1-2 дня)

### Must Have (защита диплома)
1. **Core pipeline**: Device Simulator → MQTT → Backend → ML → сцена
2. **Dashboard**: реальное время через WebSocket, карточки устройств, event log
3. **Devices**: ручное управление устройствами
4. **ML Insights**: классификатор с вероятностями, история решений

### Nice to Have
- Pattern Review (обнаружение новых паттернов)
- Simulation page (ускоренная симуляция дня)
- Экспорт CSV
- Недельная симуляция

## Этапы разработки (план параллельных агентов)

### Этап 1 — Инфраструктура + независимые сервисы (параллельно)

**Агент A — Infra:**
- `docker-compose.yml` с 5 сервисами
- `infra/mosquitto/config/mosquitto.conf`
- SQLite schema через SQLAlchemy в `backend/`
- specs: `specs/infra/mosquitto.md`, `specs/backend/db-schema.md`

**Агент B — Device Simulator:**
- Реестр 8 устройств в памяти
- MQTT публикация/подписка (paho-mqtt)
- Исполнение 4 предустановленных сцен
- REST API для ручного управления
- specs: `specs/device-simulator/*.md`

**Агент C — ML Service:**
- Загрузка CASAS датасета и маппинг
- Random Forest классификатор
- K-Means кластеризатор
- Pattern Suggester
- REST API endpoints
- specs: `specs/ml/*.md`

### Этап 2 — Backend + Frontend skeleton (параллельно)

**Агент D — Backend API:**
- MQTT client (подписка + публикация)
- Feature vector builder
- ML coordination loop
- WebSocket manager
- REST endpoints (devices, scenarios, patterns, simulation proxy)
- JWT auth
- specs: `specs/backend/*.md`

**Агент E — Frontend skeleton:**
- Vite + React 18 + TypeScript + Tailwind setup
- JWT auth flow (login page, token storage)
- Sidebar layout с 6 разделами
- WebSocket hook
- specs: `specs/frontend/auth-layout.md`

### Этап 3 — Интеграция (последовательно)

- Поднимаем docker-compose
- E2E smoke-тест: симулируем событие → проверяем ML решение → сцена активирована
- Исправляем межсервисные контракты

### Этап 4 — Frontend страницы (параллельно где возможно)

- Dashboard (WebSocket + карточки + event log)
- Devices page (управление)
- ML Insights (графики, таблица решений)

## MQTT Топики

| Топик                         | Направление         | Payload               |
|-------------------------------|---------------------|-----------------------|
| `homeiq/devices/{id}/state`   | Simulator → Backend | `{"value": ...}`      |
| `homeiq/devices/{id}/command` | Backend → Simulator | `{"value": ...}`      |
| `homeiq/scenes/activate`      | Backend → Simulator | `{"scene": "day"}`    |
| `homeiq/scenes/confirmed`     | Simulator → Backend | `{"scene": "day"}`    |
| `homeiq/simulation/control`   | Backend → Simulator | `{"action": "start"}` |
| `homeiq/simulation/status`    | Simulator → Backend | `{"time": "08:00"}`   |

## Авторизация

JWT, один пользователь:
- login: `admin`
- password: `homeiq2026`

Все endpoints кроме `/auth/login` требуют `Authorization: Bearer <token>`.

## Конфигурация через ENV

```env
# Backend
MQTT_HOST=mosquitto
MQTT_PORT=1883
ML_SERVICE_URL=http://ml-service:8001
DATABASE_URL=sqlite:///data/homeiq.db
JWT_SECRET=homeiq-secret-2026
ML_CONFIDENCE_THRESHOLD=0.7

# ML Service
MODEL_PATH=data/models/
CASAS_DATA_PATH=data/casas/

# Device Simulator
MQTT_HOST=mosquitto
MQTT_PORT=1883
```

## Правила для агентов

1. **Сначала spec, потом код** — создай `specs/<layer>/<task>.md` перед любой реализацией
2. **RED первым** — напиши падающий тест перед реализацией
3. **Минимальная реализация** — только то, что нужно для GREEN
4. **Feature Schema неизменна** — 8 признаков, те же имена везде
5. **MQTT топики строго по таблице** — никаких отклонений
6. **ENV для конфигурации** — никаких хардкодов host/port/secret
7. **Каждый сервис — отдельный `requirements.txt`** или `package.json`
