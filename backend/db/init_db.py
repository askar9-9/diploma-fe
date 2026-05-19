import json
from datetime import datetime

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base, Device, Scenario

_PRESET_SCENARIOS = [
    {
        "id": "day",
        "display_name": "День",
        "commands": {"ceiling_light": 1, "bedside_light": 0, "light_level": 100, "thermostat": 22, "tv_on": 0},
    },
    {
        "id": "night",
        "display_name": "Ночь",
        "commands": {"ceiling_light": 0, "bedside_light": 1, "light_level": 10, "thermostat": 20, "tv_on": 0},
    },
    {
        "id": "away",
        "display_name": "Никого нет",
        "commands": {"ceiling_light": 0, "bedside_light": 0, "light_level": 0, "thermostat": 17, "tv_on": 0},
    },
    {
        "id": "movie",
        "display_name": "Кино",
        "commands": {"ceiling_light": 0, "bedside_light": 0, "light_level": 20, "thermostat": 22, "tv_on": 1},
    },
]

_PRESET_DEVICES = [
    {"id": "motion_hall",   "name": "Датчик коридора",  "device_type": "binary", "state": 0.0},
    {"id": "motion_living", "name": "Датчик гостиной",  "device_type": "binary", "state": 0.0},
    {"id": "temperature",   "name": "Температура",      "device_type": "float",  "state": 22.0},
    {"id": "light_level",   "name": "Освещённость",     "device_type": "float",  "state": 0.0},
    {"id": "ceiling_light", "name": "Потолочный свет",  "device_type": "binary", "state": 0.0},
    {"id": "bedside_light", "name": "Ночник",           "device_type": "binary", "state": 0.0},
    {"id": "thermostat",    "name": "Термостат",        "device_type": "float",  "state": 22.0},
    {"id": "tv_on",         "name": "Телевизор",        "device_type": "binary", "state": 0.0},
]


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        now = datetime.utcnow()

        existing_scenario_ids = {s.id for s in session.query(Scenario.id).all()}
        for data in _PRESET_SCENARIOS:
            if data["id"] not in existing_scenario_ids:
                session.add(Scenario(
                    id=data["id"],
                    display_name=data["display_name"],
                    commands=json.dumps(data["commands"]),
                    is_custom=False,
                    created_at=now,
                ))

        existing_device_ids = {d.id for d in session.query(Device.id).all()}
        for data in _PRESET_DEVICES:
            if data["id"] not in existing_device_ids:
                session.add(Device(
                    id=data["id"],
                    name=data["name"],
                    device_type=data["device_type"],
                    state=data["state"],
                    updated_at=now,
                ))

        session.commit()
    finally:
        session.close()
