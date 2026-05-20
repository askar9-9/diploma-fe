# Spec: Frontend HA Redesign + Accessibility

## Назначение
Полный редизайн фронтенда под Home Assistant-стиль:
- Удалить ML-сценарии, паттерны, ML-insights (кроме энергопрогноза)
- Добавить комнатный вид с Xiaomi-карточками устройств
- Применить 12 исправлений доступности WCAG 2.1 AA
- HA-стиль именования сущностей в UI

## Стек
React 18 + TypeScript + Vite + Tailwind CSS + Recharts (для графиков энергии)

---

## Страницы — что убрать

Удалить полностью (файлы + роуты + ссылки в Sidebar):
- `src/pages/ScenariosPage.tsx`
- `src/pages/PatternsPage.tsx`
- `src/pages/MLInsightsPage.tsx`
- `src/pages/SimulationPage.tsx`
- `src/api/scenariosApi.ts`
- `src/api/patternsApi.ts`
- `src/api/mlApi.ts`
- `src/api/simulationApi.ts`

---

## Страницы — что оставить/переделать

### Sidebar навигация (новая)
```
- Dashboard (/)
- Устройства (/devices)
- Комнаты (/areas)
- Энергия (/energy)
```

### DashboardPage (`/`)
- Карточки статистики: всего устройств, онлайн/офлайн, активных комнат, текущее потребление кВт
- Секция "Комнаты" — 6 AreaCard с количеством устройств
- Секция "Активные устройства" — EntityCard для switch/light со state="on"
- WebSocket real-time обновления
- Все тексты на русском

### DevicesPage (`/devices`)
Полный редизайн:
- Фильтр по комнате (tabs или select: Все / Прихожая / Гостиная / Кухня / Спальня / Ванная / Улица / Котельная)
- Фильтр по домену (Все / Датчики / Устройства / Освещение)
- Каждое устройство — карточка с:
  - entity_id в стиле HA (`binary_sensor.motion_hallway`)
  - Название модели (`Xiaomi Mi Motion Sensor 2`)
  - Номер модели (`RTCGQ02LM`)
  - Иконка домена (motion, door, temperature, switch, light)
  - Текущее состояние (`on`/`off` или числовое значение + ед. изм.)
  - Цветной индикатор активности
  - Кнопка управления (toggle для switch/light, нет для sensor/binary_sensor)
  - Ссылка на документацию (внешняя, target="_blank", rel="noopener")
- Кнопка "Добавить устройство" (FAB) → модальный диалог:
  - Поля: entity_id, name, model, domain (select), room (select), doc_url
  - POST /entities
  - После успеха — обновить список

### AreasPage (`/areas`)
- 6 карточек комнат: Прихожая, Гостиная, Кухня, Спальня, Ванная, Улица, Котельная
- Клик на комнату → раскрывается список устройств в этой комнате
- Для каждого устройства: иконка, entity_id, state, кнопка toggle (если управляемое)

### EnergyPage (`/energy`) — заменить EnergyDashboard
HA Energy Dashboard стиль:
- График 1: "Потребление за 7 дней" — bar chart по дням (кВт·ч/день), данные из GET /energy/history
- График 2: "Прогноз на 24 часа" — line chart с 24 точками (кВт по часам), данные из GET /hems/forecast
  - Две линии: `load_forecast` (синяя) + `solar_forecast` (жёлтая)
- Карточки: тариф сейчас, рекомендация, статус батареи (данные из GET /hems/status)
- Breakdown таблица: потребление по устройствам (switch.*) из GET /entities + их power_kw
- Все подписи на русском: "Нагрузка", "Солнечная генерация", "кВт·ч"

---

## API контракты (фронтенд → бэкенд)

### GET /entities
```typescript
interface Entity {
  entity_id: string;          // "binary_sensor.motion_hallway"
  name: string;               // "Xiaomi Mi Motion Sensor 2"
  model: string;              // "RTCGQ02LM"
  domain: string;             // "binary_sensor" | "sensor" | "switch" | "light" | "climate"
  room: string;               // "hallway" | "living" | "kitchen" | "bedroom" | "bathroom" | "outdoor" | "utility"
  room_ru: string;            // "Прихожая"
  state: string;              // "on" | "off" | "21.5"
  attributes: Record<string, unknown>;
  doc_url: string;
  power_kw: number;
  updated_at: string;
}
```

### POST /entities
```typescript
interface CreateEntityRequest {
  entity_id: string;
  name: string;
  model: string;
  domain: string;
  room: string;
  doc_url: string;
}
```

### POST /entities/{entity_id}/command
```typescript
interface EntityCommandRequest {
  state: string;  // "on" | "off" | "21.5"
}
```

### GET /areas
```typescript
interface Area {
  id: string;
  name_ru: string;
  entities: string[];  // entity_ids
}
```

### GET /hems/forecast
```typescript
interface HemsForecast {
  load_forecast: number[];   // 24 значения кВт
  solar_forecast: number[];  // 24 значения кВт
  hours: number[];           // [0..23]
}
```

### GET /hems/status
```typescript
interface HemsStatus {
  current_hour: number;
  tariff_zone: string;        // "day" | "night"
  tariff_price: number;
  optimizer_action: string;   // "charge" | "discharge" | "idle"
  recommendation: string;
}
```

### GET /energy/history
```typescript
interface EnergyHistory {
  days: Array<{
    date: string;       // "2026-05-14"
    total_kwh: number;
  }>;
}
```

### WebSocket `/ws`
Сообщения приходят в формате:
```typescript
interface WsMessage {
  type: "state_changed";
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
}
```

---

## Исправления доступности WCAG 2.1 AA (все обязательны)

1. `text-gray-400` → `text-gray-500` везде (контраст 4.83:1)
2. Все декоративные lucide-иконки: `aria-hidden="true"`
3. Цветные точки-индикаторы: `aria-hidden="true"`
4. `focus:outline-none` → `focus:ring-2 focus:ring-blue-500` на всех интерактивных элементах
5. AreaCard убрать `cursor-pointer` без `onClick`
6. Кнопки устройств: `focus:ring-2 focus:ring-blue-500 focus:ring-offset-1`
7. `<html lang="ru">` в `index.html`
8. `<title>HomeIQ — Система управления умным домом</title>` в `index.html`
9. Поля логина: `<label htmlFor=...>` с `sr-only` + `id` на inputs
10. Ошибка входа: `role="alert"`
11. "Online"/"Offline" → "Подключён"/"Отключён" в TopBar
12. `<nav aria-label="Основная навигация">`, `role="status" aria-live="polite"` для статуса WS, спиннер `aria-label="Загрузка..."`
13. Range-input термостата (если остался): `aria-label`, `aria-valuemin/max/now`

---

## Компоненты Xiaomi (устройства)

Иконки по домену (lucide-react):
- `binary_sensor` + device_class=motion → `Activity`
- `binary_sensor` + device_class=door → `DoorOpen`
- `binary_sensor` + device_class=smoke → `AlertTriangle`
- `sensor` + device_class=temperature → `Thermometer`
- `sensor` + device_class=humidity → `Droplets`
- `sensor` + device_class=illuminance → `Sun`
- `sensor` + device_class=power/battery → `Zap`
- `switch` → `Power`
- `light` → `Lightbulb`
- `climate` → `Thermometer`

Цвет состояния:
- `on` / числовое > 0 → зелёный `bg-green-500`
- `off` / 0 → серый `bg-gray-400`

---

## Acceptance Tests

### A1: Страницы удалены
- Given: авторизованный пользователь
- When: переход на `/scenarios`, `/patterns`, `/ml-insights`, `/simulation`
- Then: 404 или редирект на `/`

### A2: DevicesPage с Xiaomi-карточками
- Given: бэкенд возвращает 20 Xiaomi устройств
- When: открыть `/devices`
- Then: видны карточки с `entity_id`, `name`, `model`, ссылкой на `doc_url`

### A3: Фильтр по комнате
- Given: устройства загружены
- When: выбрать "Кухня"
- Then: видны только устройства с `room="kitchen"`

### A4: Добавление устройства
- Given: пользователь на `/devices`
- When: нажать FAB "Добавить", заполнить форму, отправить
- Then: POST /entities вызван, новое устройство появилось в списке

### A5: Energy Dashboard
- Given: GET /hems/forecast и GET /energy/history вернули данные
- When: открыть `/energy`
- Then: два графика (история 7 дней bar + прогноз 24ч line), карточка рекомендации

### A6: a11y
- Given: страница загружена
- When: проверить `lang`, контрасты, фокусные кольца
- Then: все 13 исправлений применены

### A7: WebSocket real-time
- Given: подключение к `/ws`
- When: приходит `{type: "state_changed", entity_id: "switch.plug_tv_living", state: "on"}`
- Then: карточка устройства обновляется без перезагрузки страницы
