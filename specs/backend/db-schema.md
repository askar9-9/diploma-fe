# Spec: Database Schema (SQLite via SQLAlchemy)

## Назначение

SQLite-база данных обеспечивает персистентное хранение всех данных системы HomeIQ. Управляется Backend через SQLAlchemy ORM. Файл БД: `data/homeiq.db` в volume контейнера.

## Контракт

### Файлы реализации
- `backend/db/models.py` — SQLAlchemy-модели (таблицы)
- `backend/db/init_db.py` — инициализация: создание таблиц + seed-данные

### Таблица: devices
| Колонка      | Тип      | Ограничения          | Описание                      |
|--------------|----------|----------------------|-------------------------------|
| id           | String   | PK                   | Идентификатор (`motion_hall`) |
| name         | String   | NOT NULL             | Отображаемое название         |
| device_type  | String   | NOT NULL             | `"binary"` или `"float"`      |
| state        | Float    | NOT NULL, default 0  | Текущее состояние             |
| updated_at   | DateTime | NOT NULL             | Время последнего обновления   |

### Таблица: events
| Колонка    | Тип      | Ограничения      | Описание                      |
|------------|----------|------------------|-------------------------------|
| id         | Integer  | PK, autoincrement| Идентификатор события         |
| device_id  | String   | FK → devices.id  | Устройство                    |
| new_state  | Float    | NOT NULL         | Новое значение состояния      |
| attributes | String   | nullable         | JSON-атрибуты события         |
| created_at | DateTime | NOT NULL         | Время события                 |

### Таблица: feature_vectors
| Колонка           | Тип      | Ограничения      | Описание                              |
|-------------------|----------|------------------|---------------------------------------|
| id                | Integer  | PK, autoincrement|                                       |
| hour_of_day       | Integer  | NOT NULL         | 0–23                                  |
| weekday           | Integer  | NOT NULL         | 0–6 (Mon=0)                           |
| motion_hall       | Integer  | NOT NULL         | 0/1                                   |
| motion_living     | Integer  | NOT NULL         | 0/1                                   |
| temperature       | Float    | NOT NULL         | 15.0–30.0                             |
| light_level       | Float    | NOT NULL         | 0.0–100.0                             |
| tv_on             | Integer  | NOT NULL         | 0/1                                   |
| minutes_idle      | Integer  | NOT NULL         | 0–480                                 |
| predicted_scenario| String   | nullable         | Предсказанный сценарий                |
| confidence        | Float    | nullable         | Уверенность модели (0.0–1.0)          |
| decision_source   | String   | nullable         | `"classifier"`, `"clusterer"`, `"manual"` |
| created_at        | DateTime | NOT NULL         | Время записи                          |

### Таблица: scenarios
| Колонка      | Тип      | Ограничения        | Описание                        |
|--------------|----------|--------------------|---------------------------------|
| id           | String   | PK                 | Идентификатор (`"day"`)         |
| display_name | String   | NOT NULL           | Отображаемое название           |
| commands     | String   | NOT NULL           | JSON целевых состояний устройств|
| is_custom    | Boolean  | NOT NULL, default False | Пользовательский сценарий  |
| created_at   | DateTime | NOT NULL           | Время создания                  |

### Таблица: suggested_patterns
| Колонка          | Тип      | Ограничения       | Описание                              |
|------------------|----------|-------------------|---------------------------------------|
| id               | Integer  | PK, autoincrement |                                       |
| cluster_id       | Integer  | NOT NULL          | Идентификатор кластера K-Means        |
| description      | String   | NOT NULL          | JSON (временное окно, дни, значения)  |
| occurrence_count | Integer  | NOT NULL          | Количество наблюдений                 |
| status           | String   | NOT NULL          | `"pending"`, `"confirmed"`, `"rejected"` |
| discovered_at    | DateTime | NOT NULL          | Время обнаружения                     |

### Seed-данные при инициализации

**4 предустановленных сценария:**

| id      | display_name   | commands (JSON)                                                           |
|---------|----------------|---------------------------------------------------------------------------|
| `day`   | День           | `{"ceiling_light":1,"bedside_light":0,"light_level":100,"thermostat":22,"tv_on":0}` |
| `night` | Ночь           | `{"ceiling_light":0,"bedside_light":1,"light_level":10,"thermostat":20,"tv_on":0}`  |
| `away`  | Никого нет     | `{"ceiling_light":0,"bedside_light":0,"light_level":0,"thermostat":17,"tv_on":0}`   |
| `movie` | Кино           | `{"ceiling_light":0,"bedside_light":0,"light_level":20,"thermostat":22,"tv_on":1}`  |

**8 устройств:**

| id             | name            | device_type | initial state |
|----------------|-----------------|-------------|---------------|
| motion_hall    | Датчик коридора | binary      | 0.0           |
| motion_living  | Датчик гостиной | binary      | 0.0           |
| temperature    | Температура     | float       | 22.0          |
| light_level    | Освещённость    | float       | 0.0           |
| ceiling_light  | Потолочный свет | binary      | 0.0           |
| bedside_light  | Ночник          | binary      | 0.0           |
| thermostat     | Термостат       | float       | 22.0          |
| tv_on          | Телевизор       | binary      | 0.0           |

## Acceptance Tests

### Тест 1: Все таблицы создаются при инициализации
- Given: пустая SQLite-база данных (`:memory:`)
- When: вызывается `init_db()`
- Then: в БД существуют таблицы `devices`, `events`, `feature_vectors`, `scenarios`, `suggested_patterns`

### Тест 2: 4 предустановленных сценария после инициализации
- Given: пустая SQLite-база данных (`:memory:`)
- When: вызывается `init_db()`
- Then: в таблице `scenarios` ровно 4 записи с id: `day`, `night`, `away`, `movie`

### Тест 3: 8 устройств после инициализации
- Given: пустая SQLite-база данных (`:memory:`)
- When: вызывается `init_db()`
- Then: в таблице `devices` ровно 8 записей

### Тест 4: Устройства имеют правильные типы
- Given: выполнена инициализация БД
- When: запрашиваем все устройства
- Then: `motion_hall`, `motion_living`, `ceiling_light`, `bedside_light`, `tv_on` имеют `device_type = "binary"`;
       `temperature`, `light_level`, `thermostat` имеют `device_type = "float"`

### Тест 5: Повторная инициализация идемпотентна
- Given: БД уже инициализирована с seed-данными
- When: вызывается `init_db()` повторно
- Then: количество записей не изменилось (нет дубликатов)
