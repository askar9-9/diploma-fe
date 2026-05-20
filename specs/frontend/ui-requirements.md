# UI/UX Requirements: HomeIQ ← Home Assistant Design Audit

> Дата аудита: 2026-05-20  
> Источник: http://localhost:8123 (Home Assistant) vs http://localhost:5173 (HomeIQ)  
> Цель: скопировать дизайн-язык и компоненты HA в HomeIQ  

**Содержание:**
- [§1–6] — Визуальный аудит, функциональные и нефункциональные требования дизайна
- [§7] — Управление устройствами: добавление, контроль, контракты полей
- [§8] — Функция автоматизации (ML-pipeline): как работает, все действия, UI

---

## 1. Результаты аудита

### 1.1 Home Assistant — что взять за эталон

| Элемент | Описание |
|---|---|
| **Тема** | Dark theme по умолчанию: `#111827` (sidebar), `#1c1c1e` (content background) |
| **Sidebar** | 220px, `bg-[#1c2636]`, иконка + текст навигации, нижний блок с Настройки / Уведомления / Профиль |
| **Header** | Только заголовок страницы слева + action-иконки справа (search, chat, edit, add) |
| **Entity cards** | Иконка с цветом состояния, название, статус badge, локация — всё на тёмном фоне |
| **Area cards** | Квадратные плитки в сетке, иконка + название комнаты |
| **Stat badges** | Компактные inline-бейджи рядом с именем |
| **Favorites** | Горизонтальный grid 2×N entity-карточек на главной |
| **История / Активность** | Таймлайн с date-range picker + фильтр по сущностям |
| **Цвета акцента** | `#03A9F4` cyan-blue (кнопки, active nav, ссылки) |
| **Typography** | Roboto / system-ui, белый текст + `#9ca3af` secondary |
| **Скруглення** | Умеренные — карточки `rounded-xl` (12px), не `rounded-3xl` |
| **Тени** | Слабые `shadow-sm` или вовсе без теней — не выбиваются из dark theme |

### 1.2 HomeIQ — текущее состояние (gap-анализ)

| Страница | Что есть | Что не соответствует HA |
|---|---|---|
| **Login** | Центрированная карточка, иконка, логин/пароль/кнопка | Светлый фон (#f1f5f9) вместо тёмного; rounded-3xl слишком крупный |
| **Dashboard** | 4 stat-карточки, grid комнат 3×N, секция активных устройств | Светлый контент; скруглення `rounded-3xl`; нет секции «Избранное»; нет правой колонки «Сводка» |
| **Устройства** | Фильтр по комнате (chips), фильтр по домену, список + FAB | Светлые карточки; FAB не в стиле HA; пустое состояние не оформлено |
| **Комнаты** | List-view со стрелкой expand | HA показывает сетку плиток, не список; нет drill-down в комнату |
| **Энергия** | 3 stat-карточки, placeholders для графиков | Нет реальных графиков; нет дат-пикера |
| **Sidebar** | 4 раздела + WebSocket indicator | Нет нижнего блока с профилем; нет иконки уведомлений |
| **TopBar** | Заголовок страницы + статус "Отключён" + admin | "Отключён" красным цветом — правильно; нет search-иконки |

---

## 2. Функциональные требования (FR)

### FR-01 — Глобальная смена темы на dark

- **Описание**: Весь UI переходит на тёмную тему в стиле HA.
- **Критерии приёмки**:
  - `body` background: `#111827` (gray-900)
  - Контент-область: `#1f2937` (gray-800)
  - Sidebar: `#0f172a` (slate-950) — без изменений, уже тёмный
  - Карточки: `#1f2937` border `#374151`
  - Основной текст: `#f9fafb`, secondary: `#9ca3af`
  - Кнопки primary: `#0ea5e9` (sky-500) в стиле HA cyan

### FR-02 — Компонент EntityCard (dark-версия)

- **Описание**: Переработать `EntityCard.tsx` под dark theme в стиле HA.
- **Критерии приёмки**:
  - Карточка: `bg-gray-800 border-gray-700 rounded-xl`
  - Иконка-аватар: цвет зависит от состояния (`active → bg-sky-900/50 text-sky-400`, `inactive → bg-gray-700 text-gray-400`)
  - Название: `text-white font-medium`
  - Статус badge: `bg-gray-700 text-gray-300 rounded-full text-xs`
  - Локация badge: `bg-sky-900/30 text-sky-400 rounded-full text-xs`
  - Кнопка toggle: `bg-sky-500 hover:bg-sky-600` (вкл) / `bg-gray-700 hover:bg-gray-600` (выкл)
  - `rounded-xl` вместо `rounded-3xl`

### FR-03 — Компонент AreaCard (dark + grid-квадрат)

- **Описание**: Переработать `AreaCard.tsx` под стиль HA (квадратная плитка, dark).
- **Критерии приёмки**:
  - Плитка: `bg-gray-800 border border-gray-700 rounded-xl` квадратная (`aspect-square` или фиксированный размер)
  - Иконка по центру, название снизу
  - Счётчик активных устройств: маленький badge в углу
  - Hover: `bg-gray-700` с плавным переходом
  - Клик ведёт на `/areas/:id` (страница комнаты)

### FR-04 — StatCard (dark-версия)

- **Описание**: Переработать `StatCard.tsx` под dark.
- **Критерии приёмки**:
  - `bg-gray-800 border-gray-700 rounded-xl`
  - Иконка: цветная (каждая карточка свой цвет — sky, green, purple, amber)
  - Значение: `text-white text-2xl font-bold`
  - Описание: `text-gray-400 text-sm`

### FR-05 — Sidebar (нижний блок профиля + уведомления)

- **Описание**: Добавить нижний блок в Sidebar по аналогии с HA.
- **Критерии приёмки**:
  - Секция под nav: разделитель `border-t border-gray-700`
  - Иконка «Настройки» со ссылкой (placeholder `/settings`)
  - Иконка «Уведомления» (placeholder)
  - Аватар / инициалы пользователя + имя
  - WebSocket indicator остаётся, перемещается в эту секцию

### FR-06 — Dashboard: секция «Избранное»

- **Описание**: На Dashboard добавить секцию «Избранное» над комнатами (аналог HA).
- **Критерии приёмки**:
  - Горизонтальный grid 2 строки × N колонок entity-карточек
  - Компактный вариант EntityCard (без кнопок, только иконка + название + статус + локация)
  - Данные: первые 6–8 entity из всех активных
  - Справа от Избранного — колонка «Сводка» (количество устройств, подключённых, active scenes)

### FR-07 — Dashboard: правая колонка «Сводка»

- **Описание**: Добавить правую панель сводки на Dashboard.
- **Критерии приёмки**:
  - Фиксированная ширина ~280px справа (скрывается на < lg)
  - Отображает: общее число entity, число активных, текущую сцену ML, статус WebSocket
  - Стиль: тёмные карточки `bg-gray-800`

### FR-08 — Страница комнаты (drill-down)

- **Описание**: Создать страницу `/areas/:areaId` для просмотра устройств в комнате.
- **Критерии приёмки**:
  - Заголовок: иконка комнаты + название + количество entity
  - Grid entity-карточек (dark, FR-02)
  - Кнопка «назад» → `/areas`
  - Фильтр по домену (chips, как на `/devices`)

### FR-09 — История (новая страница `/history`)

- **Описание**: Создать страницу истории событий по аналогии с HA Активность/История.
- **Критерии приёмки**:
  - Date-range picker (начало / конец)
  - Таймлайн событий: время + entity + изменение состояния
  - Фильтр по entity_id или room
  - Данные из `eventsApi.ts`
  - Пустое состояние оформлено (иконка + текст)

### FR-10 — Поиск (глобальный, header)

- **Описание**: Добавить кнопку поиска в TopBar (иконка 🔍), открывающую modal/spotlight.
- **Критерии приёмки**:
  - Иконка search в правой части TopBar
  - Modal с input, живой поиск по entity (name, entity_id, room)
  - Результаты: compact EntityCard
  - Закрытие: Escape или клик вне modal
  - Клавиатурная навигация (↑↓ по результатам, Enter для перехода)

### FR-11 — Страница Устройства: компактный grid-режим

- **Описание**: Добавить переключатель вида «список ↔ сетка» на странице Устройства.
- **Критерии приёмки**:
  - Кнопка-toggle в header страницы
  - Grid-режим: компактные карточки 3–4 колонки (только иконка + имя + статус)
  - Список-режим: полная EntityCard (как сейчас)
  - Выбор сохраняется в localStorage

### FR-12 — Real-time WebSocket updates

- **Описание**: Обновления состояний устройств без перезагрузки страницы.
- **Критерии приёмки**:
  - При получении `WsStateChangedMessage` обновляется состояние соответствующего entity в React-стейте
  - Карточки мигают / плавно обновляются (transition на цвете статуса)
  - Timestamp «Обновлено» пересчитывается
  - WebSocket indicator в sidebar показывает `bg-green-500` при коннекте

### FR-13 — Энергия: реальные графики

- **Описание**: Заменить placeholders на реальные графики потребления.
- **Критерии приёмки**:
  - «Потребление за 7 дней»: bar chart (recharts или chart.js), данные из `energyApi.ts`
  - «Прогноз на 24 часа»: line chart (нагрузка vs солнечная генерация)
  - Цветовая схема: тёмный фон, линии sky-blue и amber
  - Tooltip при hover по точке

---

## 3. Нефункциональные требования (NFR)

### NFR-01 — Визуальная консистентность с HA

| Свойство | Значение |
|---|---|
| Скругления карточек | `rounded-xl` (12px), не `rounded-3xl` (24px) |
| Тени | `shadow-sm` только на карточках; sidebar без теней |
| Spacing | Padding карточек `p-4` (16px), не `p-5` (20px) |
| Анимации | `transition-colors duration-150` на hover, `transition-all duration-200` на toggle |
| Иконки | Lucide React (уже используется) — сохранить библиотеку |

### NFR-02 — Цветовая система (Design Tokens)

```css
/* Объявить в tailwind.config.js или index.css */
--color-bg-base:      #111827;   /* gray-900, body */
--color-bg-elevated:  #1f2937;   /* gray-800, карточки */
--color-bg-card:      #1f2937;   /* gray-800 */
--color-border:       #374151;   /* gray-700 */
--color-text-primary: #f9fafb;   /* gray-50 */
--color-text-secondary:#9ca3af; /* gray-400 */
--color-accent:       #0ea5e9;   /* sky-500 (HA cyan) */
--color-accent-hover: #0284c7;   /* sky-600 */
--color-success:      #22c55e;   /* green-500 */
--color-warning:      #f59e0b;   /* amber-500 */
--color-error:        #ef4444;   /* red-500 */
```

### NFR-03 — Доступность (Accessibility)

- ARIA-роли на всех интерактивных элементах (`role="button"`, `aria-label`)
- Focus ring: `focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900`
- Контраст текста ≥ 4.5:1 (WCAG AA) — проверить вторичный `#9ca3af` на `#1f2937` (✓ ~5.9:1)
- `aria-live="polite"` на WebSocket status и на изменения состояния entity

### NFR-04 — Адаптивность

| Брейкпоинт | Поведение |
|---|---|
| `< lg` (< 1024px) | Sidebar сворачивается в горизонтальный nav сверху (уже частично реализовано) |
| `lg+` (≥ 1024px) | Sidebar фиксированный слева 220px, контент занимает остаток |
| `< md` (< 768px) | Stat-карточки: 2 колонки вместо 4 |
| `< sm` (< 640px) | Area/Room tiles: 2 колонки вместо 3 |

### NFR-05 — Производительность

- Lazy-load страниц через `React.lazy` + `Suspense`
- Дебаунс на WebSocket-апдейтах: batch-обновление состояний раз в 100ms
- Мемоизация тяжёлых вычислений (`useMemo` для фильтрации entity списков)
- Скелетон-загрузка вместо спиннера (компонент `SkeletonCard`)

### NFR-06 — Состояния пустоты и ошибок

| Ситуация | UI |
|---|---|
| Backend недоступен | Amber banner вверху страницы (как в текущем HomeIQ) + retry кнопка |
| Пустой список устройств | Иконка + «Устройства не найдены» + CTA «Добавить первое устройство» |
| Пустая комната | Иконка + «В этой комнате нет устройств» |
| WebSocket отключён | Красный dot в sidebar + «Переподключение...» при reconnect |
| Загрузка данных | Skeleton cards (серые прямоугольники анимированные) |

### NFR-07 — Кодовые ограничения

- Tailwind CSS 4.x — все стили через классы, не `style={}`
- Без CSS-in-JS (styled-components, emotion)
- Все компоненты `ui/` — без прямых API-вызовов (только пропсы)
- Страницы `pages/` — единственная точка работы с `context` и `api`
- Тесты: Vitest + RTL; покрытие ≥ 80% для `ui/` компонентов

---

## 4. Приоритизация реализации

### P0 — Критично для защиты диплома (сделать первым)

| # | Задача | Компонент | Время |
|---|---|---|---|
| 1 | Dark theme на всё приложение | `index.css`, `tailwind.config.js` | 1–2 ч |
| 2 | EntityCard dark-версия | `EntityCard.tsx` | 1 ч |
| 3 | AreaCard dark + grid | `AreaCard.tsx` | 1 ч |
| 4 | StatCard dark | `StatCard.tsx` | 30 мин |
| 5 | Real-time WS updates | `HomeDataContext.tsx` | 2 ч |

### P1 — Важно для демонстрации

| # | Задача | Компонент | Время |
|---|---|---|---|
| 6 | Dashboard секция «Избранное» | `DashboardPage.tsx` | 2 ч |
| 7 | Sidebar: нижний блок профиля | `Sidebar.tsx` | 1 ч |
| 8 | Страница комнаты (drill-down) | `AreaDetailPage.tsx` (новая) | 3 ч |
| 9 | Энергия: реальные графики | `EnergyPage.tsx` + recharts | 3 ч |

### P2 — Nice to have

| # | Задача | Компонент | Время |
|---|---|---|---|
| 10 | Глобальный поиск | `SearchModal.tsx` (новый) | 3 ч |
| 11 | История событий `/history` | `HistoryPage.tsx` (новая) | 4 ч |
| 12 | Grid/list toggle на Устройствах | `DevicesPage.tsx` | 1 ч |
| 13 | Skeleton loading states | `SkeletonCard.tsx` (новый) | 2 ч |

---

## 5. Компоненты к созданию / переработке

### Новые файлы

```
frontend/src/
├── pages/
│   ├── AreaDetailPage.tsx      # FR-08 — комната drill-down
│   └── HistoryPage.tsx         # FR-09 — история событий
├── components/
│   ├── ui/
│   │   ├── SkeletonCard.tsx    # NFR-06 — skeleton loader
│   │   ├── CompactEntityCard.tsx # FR-06 — компактная карточка для Избранного
│   │   └── SearchModal.tsx     # FR-10 — глобальный поиск
│   └── layout/
│       └── RightSidebar.tsx    # FR-07 — правая колонка сводки
```

### Переработка существующих

```
frontend/src/
├── index.css               # NFR-02 — dark theme base styles
├── tailwind.config.js      # NFR-02 — design tokens
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx     # FR-05 — нижний блок
│   │   └── TopBar.tsx      # FR-10 — search icon
│   └── ui/
│       ├── EntityCard.tsx  # FR-02 — dark theme
│       ├── AreaCard.tsx    # FR-03 — dark + square grid
│       └── StatCard.tsx    # FR-04 — dark theme
├── pages/
│   ├── DashboardPage.tsx   # FR-06, FR-07
│   ├── DevicesPage.tsx     # FR-11
│   └── EnergyPage.tsx      # FR-13
└── App.tsx                 # добавить route /areas/:id, /history
```

---

## 6. Сравнительная таблица HA vs HomeIQ

| Функция | Home Assistant | HomeIQ сейчас | HomeIQ цель |
|---|---|---|---|
| Тема | Dark | Light content | Dark (P0) |
| Sidebar ширина | 220px | 288px (w-72) | 220px (w-56) |
| Навигация | 8+ разделов | 4 раздела | 4+2 (+ История, Поиск) |
| Профиль в sidebar | ✅ | ❌ | ✅ P1 |
| Entity cards | Dark, compact | Light, verbose | Dark, compact P0 |
| Area cards | Square grid | List | Square grid P0 |
| Избранное на главной | ✅ | ❌ | ✅ P1 |
| Поиск | ✅ Spotlight | ❌ | ✅ P2 |
| История | ✅ | ❌ | ✅ P2 |
| Реальные графики | ✅ | ❌ (placeholders) | ✅ P1 |
| Real-time updates | ✅ | Частично (WS hook) | ✅ P0 |
| Drill-down комнаты | ✅ | ❌ | ✅ P1 |
| Responsive | ✅ | Частично | ✅ P0 |
| Скелетон-загрузка | ✅ | ❌ (spinner) | ✅ P2 |
| Уведомления | ✅ | ❌ | P2 |

---

## 7. Управление устройствами: добавление и контроль

### 7.1 Обзор flow

```
Пользователь
    │
    ├─► [Нажать «+ Добавить устройство» (FAB)]
    │       └─► Открывается Modal / Drawer
    │               └─► Заполнить форму → POST /entities → запись в SQLite
    │                       └─► Refresh контекста → карточка появляется в списке
    │
    └─► [Нажать «Включить» / «Выключить» на EntityCard]
            └─► POST /entities/{entity_id}/command {"state": "on"|"off"}
                    ├─► Optimistic update в React state (мгновенно)
                    ├─► Backend → MQTT publish homeiq/{domain}/{name}/set
                    └─► Simulator получает команду → обновляет физическое состояние
                            └─► MQTT publish homeiq/{domain}/{name}/state
                                    └─► Backend → WebSocket broadcast state_changed
                                            └─► Frontend обновляет карточку
```

---

### 7.2 Контракты полей — Entity (полная схема)

#### TypeScript (Frontend)

```typescript
// src/types/home.ts

export interface Entity {
  entity_id: string          // "binary_sensor.motion_hallway" — уникальный PK
  name:      string          // "Xiaomi Mi Motion Sensor 2"
  model:     string          // "RTCGQ02LM"
  domain:    EntityDomain    // см. ниже
  room:      RoomId          // см. ниже
  room_ru:   string          // "Прихожая" — локализованное название
  state:     string          // "on" | "off" | "21.5" | "unknown" | "unavailable"
  attributes: Record<string, unknown> // device_class, unit_of_measurement, color_mode, ...
  doc_url:   string          // URL на документацию производителя
  power_kw:  number          // Номинальная мощность в кВт (0.0 для датчиков)
  updated_at: string         // ISO 8601 datetime, например "2026-05-20T14:30:00Z"
}

export type EntityDomain =
  | 'binary_sensor'   // Бинарный датчик (motion, door, smoke)
  | 'sensor'          // Числовой датчик (temperature, humidity, illuminance, power, battery)
  | 'switch'          // Управляемое реле/розетка
  | 'light'           // Управляемый свет
  | 'climate'         // Термостат/климат-контроль

export type RoomId =
  | 'hallway'   // Прихожая
  | 'living'    // Гостиная
  | 'kitchen'   // Кухня
  | 'bedroom'   // Спальня
  | 'bathroom'  // Ванная
  | 'outdoor'   // Улица
  | 'utility'   // Котельная

// Для создания устройства (POST /entities)
export interface CreateEntityRequest {
  entity_id: string    // обязательный, уникальный
  name:      string    // обязательный
  model:     string    // опциональный, default ""
  domain:    EntityDomain  // обязательный
  room:      RoomId    // обязательный
  doc_url:   string    // опциональный, default ""
  power_kw?: number    // опциональный, default 0.0
}

// Команда управления (POST /entities/{entity_id}/command)
export interface EntityCommandRequest {
  state: string        // "on" | "off" | числовое значение как строка ("21.5")
}
```

#### Поле `attributes` — допустимые ключи по домену

| domain | device_class | unit_of_measurement | доп. ключи |
|---|---|---|---|
| `binary_sensor` | `"motion"` \| `"door"` \| `"smoke"` | — | `available: boolean` |
| `sensor` (temp) | `"temperature"` | `"°C"` | — |
| `sensor` (влажн.) | `"humidity"` | `"%"` | — |
| `sensor` (свет) | `"illuminance"` | `"lx"` | — |
| `sensor` (мощн.) | `"power"` | `"kW"` | — |
| `sensor` (батар.) | `"battery"` | `"%"` | — |
| `switch` | `"plug"` | — | — |
| `light` | — | — | `color_mode: "color_temp"\|"brightness"`, `brightness: 0-255` |
| `climate` | `"temperature"` | `"°C"` | `min: 17`, `max: 25`, `target_temp: float` |

#### Правила валидации `entity_id`

```
Формат:  {domain}.{snake_case_name}
Regex:   ^(binary_sensor|sensor|switch|light|climate)\.[a-z][a-z0-9_]{2,63}$
Примеры: binary_sensor.motion_hallway  ✓
         switch.plug_tv_living         ✓
         Switch.TV                     ✗ (uppercase)
         sensor.x                      ✗ (слишком короткий name)
```

---

### 7.3 Backend REST API — полные контракты

#### `GET /entities`
```
Authorization: Bearer <jwt>
Response 200:
[
  {
    "entity_id":  "binary_sensor.motion_hallway",
    "name":       "Xiaomi Mi Motion Sensor 2",
    "model":      "RTCGQ02LM",
    "domain":     "binary_sensor",
    "room":       "hallway",
    "room_ru":    "Прихожая",
    "state":      "off",
    "attributes": {"device_class": "motion"},
    "doc_url":    "https://www.mi.com/global/product/xiaomi-mi-motion-sensor-2",
    "power_kw":   0.0,
    "updated_at": "2026-05-20T14:00:00Z"
  },
  ...
]
```

#### `POST /entities`
```
Authorization: Bearer <jwt>
Content-Type: application/json
Body:
{
  "entity_id": "switch.plug_tv_living",
  "name":      "Xiaomi Mi Smart Plug 2",
  "model":     "ZNCZ04LM",
  "domain":    "switch",
  "room":      "living",
  "doc_url":   "https://www.mi.com/global/product/xiaomi-smart-plug2",
  "power_kw":  0.15
}

Response 201: <EntitySchema>
Response 409: {"detail": "entity_id already exists"}
Response 422: Pydantic validation error
```

#### `DELETE /entities/{entity_id}`
```
Authorization: Bearer <jwt>
Response 200: {"deleted": "switch.plug_tv_living"}
Response 404: {"detail": "Entity not found"}
```

#### `POST /entities/{entity_id}/command`
```
Authorization: Bearer <jwt>
Body: {"state": "on"}

Response 200: {"status": "ok", "entity_id": "switch.plug_tv_living", "state": "on"}
Response 404: {"detail": "Entity not found"}
Response 400: {"detail": "Entity domain switch is not controllable"}
              (только switch и light принимают команды on/off)
```

#### `GET /areas`
```
Authorization: Bearer <jwt>
Response 200:
[
  {
    "id":       "hallway",
    "name_ru":  "Прихожая",
    "entities": ["binary_sensor.motion_hallway", "binary_sensor.door_hallway", "switch.plug_light_hallway"]
  },
  ...
]
```

---

### 7.4 Функциональные требования — добавление устройства (FR-DEV-01)

**Описание:** Диалог добавления нового устройства через форму в стиле HA.

**UX Flow:**
1. FAB `+ Добавить устройство` → открывается Modal (drawer на мобильном)
2. Форма с 6 полями (см. §7.2 `CreateEntityRequest`)
3. Валидация `entity_id` по regex в реальном времени (inline error под полем)
4. `domain` — select, значение определяет иконку в превью карточки
5. `room` — select с русскими названиями
6. Submit → `POST /entities` → success: закрыть, toast «Устройство добавлено» → refresh
7. Error 409 → inline: «Entity ID уже занят. Выберите другой.»

**Поля формы:**

| Поле UI | Имя в запросе | Тип | Обязательное | Placeholder | Валидация |
|---|---|---|---|---|---|
| Entity ID | `entity_id` | text | ✅ | `binary_sensor.motion_hallway` | regex, уникальность |
| Название | `name` | text | ✅ | `Xiaomi Mi Motion Sensor 2` | min 2 символа |
| Модель | `model` | text | ❌ | `RTCGQ02LM` | — |
| Домен | `domain` | select | ✅ | — | из DOMAIN_OPTIONS |
| Комната | `room` | select | ✅ | — | из ROOM_OPTIONS |
| Ссылка на документацию | `doc_url` | url | ❌ | `https://...` | valid URL или пусто |
| Мощность (кВт) | `power_kw` | number | ❌ | `0.15` | ≥ 0, ≤ 50 |

---

### 7.5 Функциональные требования — управление устройством (FR-DEV-02)

**Описание:** Управление состоянием controllable entity (switch, light) с карточки.

**Controllable домены:** `switch`, `light`  
**Некontrollable домены:** `binary_sensor`, `sensor`, `climate` (только read-only отображение)

**UX Flow — Toggle:**
1. Пользователь нажимает кнопку «Включить» / «Выключить» на EntityCard
2. Кнопка немедленно переходит в состояние loading (спиннер)
3. Optimistic update: карточка показывает новое состояние (до ответа сервера)
4. `POST /entities/{entity_id}/command {"state": "on"|"off"}`
5. При успехе: состояние зафиксировано
6. При ошибке: откат к предыдущему состоянию + toast «Не удалось выполнить команду»

**UX Flow — Climate (термостат):**
1. На карточке климата показывается текущая температура + кнопки `-` / `+`
2. Диапазон: 17°C – 25°C (из `attributes.min` / `attributes.max`)
3. `POST /entities/climate.thermostat_main/command {"state": "21.5"}`
4. Debounce 500ms перед отправкой (чтобы не спамить при нажатии)

**UX Flow — Light с яркостью:**
1. На карточке light показывается слайдер яркости 0–100%
2. `POST /entities/{entity_id}/command {"state": "on", "brightness": 200}`
3. `brightness` передаётся в `attributes` тела запроса (расширение EntityCommandRequest)

**Состояния кнопки toggle:**

| Состояние | Визуал кнопки | Цвет |
|---|---|---|
| Entity OFF → нажать «Включить» | Иконка Power + «Включить» | `bg-sky-500` |
| Ожидание ответа | Спиннер + «Включить» | `bg-sky-500 opacity-60` |
| Entity ON | Иконка Power + «Выключить» | `bg-gray-700` |
| Ошибка | Иконка AlertCircle + «Ошибка» | `bg-red-600` (2 сек, затем откат) |
| Entity unavailable | Кнопка disabled | `opacity-30 cursor-not-allowed` |

---

### 7.6 Функциональные требования — удаление устройства (FR-DEV-03)

**Описание:** Удаление entity из системы.

**UX Flow:**
1. На EntityCard кнопка `⋮` (kebab menu) → пункт «Удалить»
2. Confirm dialog: «Удалить {name}? Это действие необратимо.»
3. Кнопки: «Удалить» (red) / «Отмена»
4. `DELETE /entities/{entity_id}` → success: toast «Устройство удалено» → убрать из списка
5. При ошибке: toast «Не удалось удалить»

---

### 7.7 Устройства системы HomeIQ (Device Simulator — 8 devices)

Это **физические устройства** Device Simulator, отдельно от HA-entities. Они публикуют состояния через MQTT.

```typescript
// src/api/devicesApi.ts
export interface Device {
  id:          string   // "motion_hall" | "motion_living" | "temperature" | ...
  name:        string   // Human-readable name
  device_type: string   // "binary" (0|1) | "float" (число)
  state:       number   // Текущее значение
  updated_at:  string   // ISO timestamp
}
```

**Реестр устройств:**

| device_id | device_type | Диапазон | Описание |
|---|---|---|---|
| `motion_hall` | binary | 0 / 1 | Датчик движения в прихожей |
| `motion_living` | binary | 0 / 1 | Датчик движения в гостиной |
| `temperature` | float | 15.0–30.0 | Температура воздуха (°C) |
| `light_level` | float | 0.0–100.0 | Уровень освещённости (%) |
| `ceiling_light` | binary | 0 / 1 | Потолочный свет |
| `bedside_light` | binary | 0 / 1 | Прикроватный свет |
| `thermostat` | float | 17.0–25.0 | Термостат (°C) |
| `tv_on` | binary | 0 / 1 | Телевизор |

**API команды:**
```
GET  /devices                            → список всех Device
POST /devices/{device_id}/command        → {"value": 1} или {"value": 21.5}
```

---

## 8. Функция автоматизации (ML-Pipeline)

### 8.1 Концепция

HomeIQ содержит встроенную систему автоматизации на основе машинного обучения (Random Forest), которая **автоматически определяет сцену дома** и активирует соответствующие устройства — без ручного вмешательства пользователя.

> **Ключевая идея:** система «наблюдает» за датчиками → строит вектор признаков → ML классифицирует текущий контекст → Backend применяет сцену, выставляя состояния устройств.

---

### 8.2 Полный pipeline (шаг за шагом)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         АВТОМАТИЗАЦИЯ HomeIQ                           │
└─────────────────────────────────────────────────────────────────────────┘

Шаг 1 ─ Датчики публикуют состояния
   Device Simulator (каждые N секунд или при изменении)
       → MQTT: homeiq/devices/{device_id}/state
       → payload: {"value": 1}  (или float)

Шаг 2 ─ Backend получает событие
   MQTT Handler подписан на homeiq/devices/+/state
       → Сохраняет в таблицу devices (SQLite)
       → Сохраняет в таблицу events (история изменений)
       → Рассылает WebSocket → Frontend обновляет карточки в реальном времени

Шаг 3 ─ Backend строит Feature Vector (8 признаков)
   build_feature_vector(current_device_states) → dict
       {
         "hour_of_day":   14,      ← из системных часов (или sim-времени)
         "weekday":       1,       ← 0=ПН, 6=ВС
         "motion_hall":   1,       ← из devices["motion_hall"].state
         "motion_living": 0,
         "temperature":   22.5,
         "light_level":   75.0,
         "tv_on":         0,
         "minutes_idle":  0        ← 0 если motion активен, иначе мин с последнего движения
       }

Шаг 4 ─ Backend вызывает ML Service
   POST http://ml-service:8001/classify
   Body: { "features": { ...feature_vector } }

   ML Service (Random Forest):
       → Загружает обученную модель из data/models/
       → Вычисляет вероятности классов
       → Возвращает:
         {
           "scenario":     "day",           ← predicted class
           "confidence":   0.87,            ← max probability
           "probabilities": {
             "day":   0.87,
             "night": 0.08,
             "away":  0.03,
             "movie": 0.02
           },
           "alternative": "night"           ← второй по вероятности класс
         }

Шаг 5 ─ Backend принимает решение
   Если confidence >= ML_CONFIDENCE_THRESHOLD (default: 0.7):
       → Активировать сцену
   Иначе:
       → Пропустить (недостаточная уверенность)
       → Сохранить в ml_history со статусом "skipped"

Шаг 6 ─ Активация сцены
   Backend публикует MQTT: homeiq/scenes/activate
   payload: {"scene": "day"}

   Device Simulator получает команду:
       → Применяет preset сцены ко всем устройствам:

   ┌─────────┬───────────────┬───────────────┬─────────────┬────────────┬───────┐
   │ Сцена   │ ceiling_light │ bedside_light │ light_level │ thermostat │ tv_on │
   ├─────────┼───────────────┼───────────────┼─────────────┼────────────┼───────┤
   │ day     │ 1             │ 0             │ 100         │ 22         │ 0     │
   │ night   │ 0             │ 1             │ 10          │ 20         │ 0     │
   │ away    │ 0             │ 0             │ 0           │ 17         │ 0     │
   │ movie   │ 0             │ 0             │ 20          │ 22         │ 1     │
   └─────────┴───────────────┴───────────────┴─────────────┴────────────┴───────┘

Шаг 7 ─ Подтверждение сцены
   Device Simulator публикует: homeiq/scenes/confirmed
   payload: {"scene": "day"}

   Backend:
       → Обновляет current_scene в памяти
       → Сохраняет в ml_history (статус "applied")
       → WebSocket broadcast: {"type": "scene_changed", "scene": "day", "confidence": 0.87}

Шаг 8 ─ Frontend получает обновление
   WebSocket message type: "scene_changed"
       → Обновляет индикатор «Текущая сцена» на Dashboard
       → Добавляет запись в Event Log
       → Toast notification: «Сцена "День" активирована (87%)»
```

---

### 8.3 Feature Vector — детальное описание полей

| Признак | Тип | Диапазон | Источник | Описание |
|---|---|---|---|---|
| `hour_of_day` | int | 0–23 | Системные часы | Час суток. Ключевой признак — «ночь» (0–6), «утро» (7–11), «день» (12–17), «вечер» (18–23) |
| `weekday` | int | 0–6 | Системные часы | День недели (0=ПН, 6=ВС). Паттерны выходного и рабочего дня различаются |
| `motion_hall` | int | 0 / 1 | Device: `motion_hall` | Движение в прихожей. 1 = кто-то пришёл/ушёл → признак «away→home» |
| `motion_living` | int | 0 / 1 | Device: `motion_living` | Движение в гостиной. 1 + tv_on → признак «movie» |
| `temperature` | float | 15.0–30.0 | Device: `temperature` | Температура помещения. Коррелирует с временем суток и сезоном |
| `light_level` | float | 0.0–100.0 | Device: `light_level` | Естественная освещённость. Низкая = вечер/ночь |
| `tv_on` | int | 0 / 1 | Device: `tv_on` | Телевизор включён. В сочетании с movement → «movie» |
| `minutes_idle` | int | 0–480 | Backend: computed | Минут с последнего зафиксированного движения. >60 → признак «away» |

---

### 8.4 ML Model — технические детали

| Параметр | Значение |
|---|---|
| Алгоритм | Random Forest Classifier (sklearn) |
| Датасет | CASAS Smart Home Dataset (WSU) |
| Скрипт маппинга | `ml-service/scripts/prepare_casas.py` |
| Хранение модели | `ml-service/data/models/{timestamp}.joblib` |
| Классы | `day`, `night`, `away`, `movie` |
| Порог уверенности | `ML_CONFIDENCE_THRESHOLD=0.7` (env) |
| Частота inference | При каждом изменении состояния устройства |

**REST API ML Service:**

```
POST /classify
Body:  {"features": {8 признаков}}
Response: {
  "scenario":     "day",
  "confidence":   0.87,
  "probabilities": {"day":0.87, "night":0.08, "away":0.03, "movie":0.02},
  "alternative":  "night"
}

POST /cluster
Body:  {"vectors": [...], "n_clusters": 4}
Response: {"labels": [...], "centroids": [...]}

POST /suggest
Body:  {"vectors": [...], "labels": [...], "known": ["day","night","away","movie"]}
Response: [{"pattern_id": "...", "description": "...", "example": {...}}]
```

---

### 8.5 UI требования — страница автоматизации / ML Insights (FR-AUTO-01)

**Описание:** Новая страница `/automation` или вкладка на Dashboard, показывающая работу ML pipeline.

**Навигационный пункт:** «Автоматизация» или «ML Insights» с иконкой `Brain` / `Cpu`

#### Секция 1 — Текущий статус

```
┌─────────────────────────────────────────────────────┐
│  🤖 Активная сцена                                  │
│  ─────────────────────────────────────────────────  │
│  [day]  День                          87% уверен.   │
│  Альтернатива: night (8%)                           │
│  Последнее решение: 14:32 (3 мин назад)             │
└─────────────────────────────────────────────────────┘
```

| Элемент | Описание |
|---|---|
| Бейдж сцены | Цветной badge: `day`=amber, `night`=indigo, `away`=gray, `movie`=purple |
| Прогресс-бар уверенности | Горизонтальный bar 0–100%, цвет: ≥70% green, 50–69% amber, <50% red |
| Альтернатива | Второй класс с его вероятностью |
| Timestamp | Когда было последнее ML-решение |

#### Секция 2 — Feature Vector (текущий)

Таблица 8 строк: имя признака → текущее значение → визуальный индикатор

```
┌──────────────────┬─────────┬──────────────────────┐
│ Признак          │ Значение│ Индикатор            │
├──────────────────┼─────────┼──────────────────────┤
│ hour_of_day      │ 14      │ ████████░░ (14/24)   │
│ weekday          │ 1 (Вт)  │ Вт                   │
│ motion_hall      │ 0       │ 🔴 Нет движения      │
│ motion_living    │ 1       │ 🟢 Движение есть     │
│ temperature      │ 22.5°C  │ ████████░░           │
│ light_level      │ 75%     │ ███████░░░           │
│ tv_on            │ 0       │ 🔴 Выкл              │
│ minutes_idle     │ 0       │ — (движение активно) │
└──────────────────┴─────────┴──────────────────────┘
```

#### Секция 3 — История решений ML (последние 20)

Таблица с пагинацией:

```
┌────────────┬─────────┬────────────┬────────────┬──────────┐
│ Время      │ Сцена   │ Уверенность│ Статус     │ Причина  │
├────────────┼─────────┼────────────┼────────────┼──────────┤
│ 14:32      │ day     │ 87%        │ ✅ Применено│ auto     │
│ 14:28      │ day     │ 91%        │ ✅ Применено│ auto     │
│ 14:15      │ night   │ 62%        │ ⏭ Пропущено│ low conf │
│ 13:45      │ away    │ 78%        │ ✅ Применено│ auto     │
└────────────┴─────────┴────────────┴────────────┴──────────┘
```

#### Секция 4 — Ручная активация сцены

```
┌─────────────────────────────────────────────────────┐
│  Активировать сцену вручную                         │
│  ─────────────────────────────────────────────────  │
│  [🌞 День] [🌙 Ночь] [🏠 Дома нет] [🎬 Кино]        │
└─────────────────────────────────────────────────────┘
```

- 4 кнопки, каждая с иконкой и названием сцены
- При нажатии: confirm «Активировать сцену "День"?» → `POST /scenes/activate {"scene":"day"}`
- Текущая активная сцена подсвечена (ring + background)
- Toast: «Сцена активирована»

---

### 8.6 WebSocket сообщения — типы для автоматизации

```typescript
// Существующее:
interface WsStateChangedMessage {
  type:       'state_changed'
  entity_id:  string
  state:      string
  attributes: Record<string, unknown>
}

// Новые (добавить в types/home.ts):
interface WsSceneChangedMessage {
  type:        'scene_changed'
  scene:       'day' | 'night' | 'away' | 'movie'
  confidence:  number           // 0.0–1.0
  triggered_by: 'auto' | 'manual'
}

interface WsMlDecisionMessage {
  type:           'ml_decision'
  scenario:       string
  confidence:     number
  probabilities:  Record<string, number>
  applied:        boolean       // false если confidence < threshold
  feature_vector: Record<string, number>
}

type WsMessage =
  | WsStateChangedMessage
  | WsSceneChangedMessage
  | WsMlDecisionMessage
```

---

### 8.7 API автоматизации — контракты

#### `GET /ml/history`
```
Authorization: Bearer <jwt>
Query: ?limit=20&offset=0

Response 200:
{
  "items": [
    {
      "id":            1,
      "scenario":      "day",
      "confidence":    0.87,
      "probabilities": {"day":0.87,"night":0.08,"away":0.03,"movie":0.02},
      "applied":       true,
      "feature_vector":{"hour_of_day":14,"weekday":1,...},
      "created_at":    "2026-05-20T14:32:00Z"
    }
  ],
  "total": 142
}
```

#### `GET /ml/current-scene`
```
Authorization: Bearer <jwt>
Response 200:
{
  "scene":       "day",
  "confidence":  0.87,
  "last_decision_at": "2026-05-20T14:32:00Z"
}
```

#### `POST /scenes/activate`
```
Authorization: Bearer <jwt>
Body: {"scene": "day"}

Response 200: {"status": "ok", "scene": "day"}
Response 400: {"detail": "Unknown scene 'disco'"}
```

#### `GET /ml/feature-vector`
```
Authorization: Bearer <jwt>
Response 200:
{
  "hour_of_day":   14,
  "weekday":       1,
  "motion_hall":   0,
  "motion_living": 1,
  "temperature":   22.5,
  "light_level":   75.0,
  "tv_on":         0,
  "minutes_idle":  0
}
```

---

### 8.8 Новые Frontend файлы для автоматизации

```
frontend/src/
├── pages/
│   └── AutomationPage.tsx        # FR-AUTO-01 — страница ML Insights
├── components/
│   └── automation/
│       ├── CurrentSceneBadge.tsx # текущая сцена + уверенность
│       ├── FeatureVectorTable.tsx # таблица 8 признаков
│       ├── MlHistoryTable.tsx     # история решений
│       └── SceneActivator.tsx    # 4 кнопки ручной активации
├── api/
│   ├── mlApi.ts                  # /ml/history, /ml/current-scene, /ml/feature-vector
│   └── scenesApi.ts              # /scenes/activate
└── types/home.ts                 # + WsSceneChangedMessage, WsMlDecisionMessage
```

**Route:** добавить в `App.tsx`:
```tsx
<Route path="/automation" element={<PrivateRoute><AutomationPage /></PrivateRoute>} />
```

**Sidebar nav item:**
```typescript
{ path: '/automation', label: 'Автоматизация', icon: Brain }
```

---

### 8.9 Приоритизация автоматизации

| # | Задача | P | Время |
|---|---|---|---|
| A1 | `CurrentSceneBadge` на Dashboard (секция Сводка) | P0 | 1 ч |
| A2 | WebSocket handler для `scene_changed` и `ml_decision` | P0 | 1 ч |
| A3 | `SceneActivator` — 4 кнопки ручной активации сцены | P1 | 2 ч |
| A4 | `AutomationPage` — полная страница ML Insights | P1 | 4 ч |
| A5 | `FeatureVectorTable` — текущий вектор признаков | P1 | 2 ч |
| A6 | `MlHistoryTable` — история с пагинацией | P2 | 3 ч |
| A7 | `mlApi.ts` + `scenesApi.ts` | P1 | 1 ч |
