from sqlalchemy import inspect

from app.seed_data import INITIAL_AREAS, INITIAL_ENTITIES
from db.init_db import init_db
from db.models import Area, DeviceState, EnergyReading, Entity, MLHistory


def test_all_tables_created(engine):
    init_db(engine)
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    assert {"areas", "entities", "energy_readings", "ml_history", "device_states"} <= existing_tables


def test_seed_data_loaded(session):
    areas = session.query(Area).all()
    entities = session.query(Entity).all()

    assert len(areas) == len(INITIAL_AREAS)
    assert len(entities) == len(INITIAL_ENTITIES)


def test_known_entity_has_expected_shape(session):
    entity = session.get(Entity, "switch.plug_tv_living")

    assert entity is not None
    assert entity.domain == "switch"
    assert entity.room == "living"
    assert entity.room_ru == "Гостиная"
    assert entity.attributes["device_class"] == "plug"


def test_init_db_idempotent(engine):
    init_db(engine)
    init_db(engine)

    from sqlalchemy.orm import sessionmaker

    db = sessionmaker(bind=engine)()
    try:
        assert db.query(Area).count() == len(INITIAL_AREAS)
        assert db.query(Entity).count() == len(INITIAL_ENTITIES)
        assert db.query(EnergyReading).count() == 0
        assert db.query(MLHistory).count() == 0
        assert db.query(DeviceState).count() == 0
    finally:
        db.close()
