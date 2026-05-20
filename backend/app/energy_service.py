from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from db.models import EnergyReading, Entity

_ENERGY_DOMAINS = {"switch", "light"}
_ACTIVE_STATES = {"on", "true", "1"}


def is_active_energy_entity(entity: Entity) -> bool:
    return entity.domain in _ENERGY_DOMAINS and str(entity.state).strip().lower() in _ACTIVE_STATES


def add_energy_reading(session: Session, recorded_at: datetime | None = None) -> EnergyReading:
    timestamp = recorded_at or datetime.utcnow()
    session.flush()

    active_entities = session.query(Entity).filter(Entity.domain.in_(_ENERGY_DOMAINS)).all()
    total_kw = round(sum(entity.power_kw for entity in active_entities if is_active_energy_entity(entity)), 6)

    reading = EnergyReading(
        date=timestamp.date().isoformat(),
        hour=timestamp.hour,
        total_kwh=total_kw,
        created_at=timestamp,
    )
    session.add(reading)
    return reading
