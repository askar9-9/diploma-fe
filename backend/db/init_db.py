from datetime import datetime

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from app.seed_data import INITIAL_AREAS, INITIAL_ENTITIES
from db.models import Area, Base, Entity


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)

    session = sessionmaker(bind=engine)()
    try:
        now = datetime.utcnow()

        if session.query(Area).count() == 0:
            session.add_all(Area(**area) for area in INITIAL_AREAS)

        if session.query(Entity).count() == 0:
            session.add_all(
                Entity(
                    entity_id=entity["entity_id"],
                    name=entity["name"],
                    model=entity["model"],
                    domain=entity["domain"],
                    room=entity["room"],
                    room_ru=entity["room_ru"],
                    state=entity["state"],
                    attributes=entity["attributes"],
                    doc_url=entity["doc_url"],
                    power_kw=entity["power_kw"],
                    updated_at=now,
                )
                for entity in INITIAL_ENTITIES
            )

        session.commit()
    finally:
        session.close()
