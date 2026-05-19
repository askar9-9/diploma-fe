"""
Tests for DB schema initialization.
Spec: specs/backend/db-schema.md

RED → GREEN → REFACTOR cycle.
Uses SQLite in-memory database for isolation.
"""
import json
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# These imports will fail until models.py and init_db.py are created (RED phase)
from db.models import Base, Device, Event, FeatureVector, Scenario, SuggestedPattern
from db.init_db import init_db


@pytest.fixture
def engine():
    """In-memory SQLite engine — isolated per test."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    """Session bound to in-memory engine with initialized schema."""
    init_db(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


# ---------------------------------------------------------------------------
# Тест 1: Все таблицы создаются при инициализации
# ---------------------------------------------------------------------------

def test_all_tables_created(engine):
    """
    Given: пустая SQLite-база данных (:memory:)
    When: вызывается init_db()
    Then: в БД существуют таблицы devices, events, feature_vectors,
          scenarios, suggested_patterns
    """
    init_db(engine)
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    assert "devices" in existing_tables, "Таблица 'devices' не создана"
    assert "events" in existing_tables, "Таблица 'events' не создана"
    assert "feature_vectors" in existing_tables, "Таблица 'feature_vectors' не создана"
    assert "scenarios" in existing_tables, "Таблица 'scenarios' не создана"
    assert "suggested_patterns" in existing_tables, "Таблица 'suggested_patterns' не создана"


# ---------------------------------------------------------------------------
# Тест 2: 4 предустановленных сценария существуют после init
# ---------------------------------------------------------------------------

def test_four_default_scenarios_exist(session):
    """
    Given: пустая SQLite-база данных (:memory:)
    When: вызывается init_db()
    Then: в таблице scenarios ровно 4 записи с id: day, night, away, movie
    """
    scenarios = session.query(Scenario).all()
    scenario_ids = {s.id for s in scenarios}

    assert len(scenarios) == 4, f"Ожидалось 4 сценария, получено {len(scenarios)}"
    assert scenario_ids == {"day", "night", "away", "movie"}, (
        f"Ожидались id {{day,night,away,movie}}, получено {scenario_ids}"
    )


def test_scenario_commands_are_valid_json(session):
    """
    Given: инициализированная БД
    When: запрашиваем все сценарии
    Then: поле commands у каждого сценария — валидный JSON
    """
    scenarios = session.query(Scenario).all()
    for scenario in scenarios:
        parsed = json.loads(scenario.commands)
        assert isinstance(parsed, dict), (
            f"Сценарий '{scenario.id}': commands должен быть JSON-объектом"
        )


def test_scenario_day_commands(session):
    """
    Проверяем конкретные значения команд сценария 'day'.
    """
    day = session.query(Scenario).filter_by(id="day").one()
    commands = json.loads(day.commands)
    assert commands["ceiling_light"] == 1
    assert commands["bedside_light"] == 0
    assert commands["light_level"] == 100
    assert commands["thermostat"] == 22
    assert commands["tv_on"] == 0


def test_scenario_movie_has_tv_on(session):
    """
    Проверяем, что сценарий 'movie' включает телевизор.
    """
    movie = session.query(Scenario).filter_by(id="movie").one()
    commands = json.loads(movie.commands)
    assert commands["tv_on"] == 1
    assert commands["ceiling_light"] == 0


# ---------------------------------------------------------------------------
# Тест 3: 8 устройств существуют после init
# ---------------------------------------------------------------------------

def test_eight_devices_exist(session):
    """
    Given: пустая SQLite-база данных (:memory:)
    When: вызывается init_db()
    Then: в таблице devices ровно 8 записей
    """
    devices = session.query(Device).all()
    assert len(devices) == 8, f"Ожидалось 8 устройств, получено {len(devices)}"


def test_all_device_ids_present(session):
    """
    Given: инициализированная БД
    When: запрашиваем все устройства
    Then: присутствуют все 8 устройств с правильными id
    """
    expected_ids = {
        "motion_hall", "motion_living", "temperature", "light_level",
        "ceiling_light", "bedside_light", "thermostat", "tv_on",
    }
    devices = session.query(Device).all()
    actual_ids = {d.id for d in devices}
    assert actual_ids == expected_ids, (
        f"Отсутствуют устройства: {expected_ids - actual_ids}\n"
        f"Лишние устройства: {actual_ids - expected_ids}"
    )


# ---------------------------------------------------------------------------
# Тест 4: Устройства имеют правильные типы (binary/float)
# ---------------------------------------------------------------------------

def test_device_types_binary(session):
    """
    Given: инициализированная БД
    When: запрашиваем бинарные устройства
    Then: motion_hall, motion_living, ceiling_light, bedside_light, tv_on
          имеют device_type = "binary"
    """
    binary_ids = {"motion_hall", "motion_living", "ceiling_light", "bedside_light", "tv_on"}
    for device_id in binary_ids:
        device = session.query(Device).filter_by(id=device_id).one()
        assert device.device_type == "binary", (
            f"Устройство '{device_id}' должно иметь тип 'binary', "
            f"получено '{device.device_type}'"
        )


def test_device_types_float(session):
    """
    Given: инициализированная БД
    When: запрашиваем аналоговые устройства
    Then: temperature, light_level, thermostat имеют device_type = "float"
    """
    float_ids = {"temperature", "light_level", "thermostat"}
    for device_id in float_ids:
        device = session.query(Device).filter_by(id=device_id).one()
        assert device.device_type == "float", (
            f"Устройство '{device_id}' должно иметь тип 'float', "
            f"получено '{device.device_type}'"
        )


# ---------------------------------------------------------------------------
# Тест 5: Повторная инициализация идемпотентна
# ---------------------------------------------------------------------------

def test_init_db_idempotent(engine):
    """
    Given: БД уже инициализирована с seed-данными
    When: вызывается init_db() повторно
    Then: количество записей не изменилось (нет дубликатов)
    """
    init_db(engine)
    init_db(engine)  # Повторный вызов

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        scenarios_count = session.query(Scenario).count()
        devices_count = session.query(Device).count()
        assert scenarios_count == 4, f"Ожидалось 4 сценария, получено {scenarios_count}"
        assert devices_count == 8, f"Ожидалось 8 устройств, получено {devices_count}"
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Дополнительные структурные тесты
# ---------------------------------------------------------------------------

def test_event_has_foreign_key_to_device(session):
    """
    Given: инициализированная БД
    When: создаём событие с валидным device_id
    Then: событие сохраняется без ошибок
    """
    from datetime import datetime
    event = Event(
        device_id="motion_hall",
        new_state=1.0,
        attributes='{"source": "test"}',
        created_at=datetime.utcnow(),
    )
    session.add(event)
    session.commit()
    assert event.id is not None


def test_feature_vector_fields(session):
    """
    Given: инициализированная БД
    When: создаём feature vector со всеми 8 признаками
    Then: запись сохраняется и id присваивается
    """
    from datetime import datetime
    fv = FeatureVector(
        hour_of_day=14,
        weekday=1,
        motion_hall=0,
        motion_living=1,
        temperature=22.5,
        light_level=80.0,
        tv_on=0,
        minutes_idle=15,
        predicted_scenario="day",
        confidence=0.92,
        decision_source="classifier",
        created_at=datetime.utcnow(),
    )
    session.add(fv)
    session.commit()
    assert fv.id is not None


def test_suggested_pattern_status_values(session):
    """
    Given: инициализированная БД
    When: создаём suggested_pattern со статусом "pending"
    Then: запись сохраняется корректно
    """
    from datetime import datetime
    pattern = SuggestedPattern(
        cluster_id=2,
        description='{"hour_range": [18, 20], "weekdays": [1, 2, 3]}',
        occurrence_count=7,
        status="pending",
        discovered_at=datetime.utcnow(),
    )
    session.add(pattern)
    session.commit()
    assert pattern.id is not None
    assert pattern.status == "pending"
