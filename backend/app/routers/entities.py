from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.energy_service import add_energy_reading
from app.mqtt_handler import entity_name_from_entity_id
from app.seed_data import ROOM_RU_BY_ID
from db.models import Area, Entity


router = APIRouter(
    prefix="/entities",
    tags=["entities"],
    dependencies=[Depends(get_current_user)],
)


class EntitySchema(BaseModel):
    entity_id: str
    name: str
    model: str
    domain: str
    room: str
    room_ru: str
    state: str
    attributes: dict[str, Any]
    doc_url: str
    power_kw: float
    updated_at: str


class CreateEntityRequest(BaseModel):
    entity_id: str
    name: str
    model: str = ""
    domain: str
    room: str
    doc_url: str = ""
    power_kw: float = 0.0
    state: str = "off"
    attributes: dict[str, Any] = Field(default_factory=dict)


class EntityCommandRequest(BaseModel):
    state: str


def serialize_entity(entity: Entity) -> dict[str, object]:
    return {
        "entity_id": entity.entity_id,
        "name": entity.name,
        "model": entity.model,
        "domain": entity.domain,
        "room": entity.room,
        "room_ru": entity.room_ru,
        "state": entity.state,
        "attributes": entity.attributes or {},
        "doc_url": entity.doc_url,
        "power_kw": entity.power_kw,
        "updated_at": entity.updated_at.isoformat(),
    }


def get_room_ru(db: Session, room: str) -> str:
    area = db.get(Area, room)
    if area is not None:
        return area.name_ru

    room_ru = ROOM_RU_BY_ID.get(room)
    if room_ru is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown room",
        )

    return room_ru


@router.get("")
def list_entities(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    entities = db.query(Entity).order_by(Entity.entity_id.asc()).all()
    return [serialize_entity(entity) for entity in entities]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_entity(
    payload: CreateEntityRequest,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    existing = db.get(Entity, payload.entity_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Entity already exists",
        )

    room_ru = get_room_ru(db, payload.room)
    entity = Entity(
        entity_id=payload.entity_id,
        name=payload.name,
        model=payload.model,
        domain=payload.domain,
        room=payload.room,
        room_ru=room_ru,
        state=payload.state,
        attributes=payload.attributes,
        doc_url=payload.doc_url,
        power_kw=payload.power_kw,
        updated_at=datetime.utcnow(),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return serialize_entity(entity)


@router.delete("/{entity_id}")
def delete_entity(
    entity_id: str,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    entity = db.get(Entity, entity_id)
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found",
        )

    db.delete(entity)
    db.commit()
    return {"deleted": entity_id}


@router.post("/{entity_id}/command")
async def send_entity_command(
    entity_id: str,
    payload: EntityCommandRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    entity = db.get(Entity, entity_id)
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found",
        )

    state_changed = entity.state != payload.state
    entity.state = payload.state
    entity.updated_at = datetime.utcnow()

    if state_changed and entity.domain in {"switch", "light"}:
        add_energy_reading(db, entity.updated_at)

    db.commit()
    db.refresh(entity)

    entity_name = entity_name_from_entity_id(entity.entity_id)
    request.app.state.mqtt_handler.publish_entity_command(entity.domain, entity_name, entity.state)
    await request.app.state.ws_manager.broadcast(
        {
            "type": "state_changed",
            "entity_id": entity.entity_id,
            "state": entity.state,
            "attributes": entity.attributes or {},
        }
    )
    return {"status": "ok", "entity_id": entity.entity_id, "state": entity.state}
