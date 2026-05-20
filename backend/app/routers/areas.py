from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from db.models import Area, Entity


router = APIRouter(
    prefix="/areas",
    tags=["areas"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
def list_areas(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    areas = db.query(Area).order_by(Area.id.asc()).all()
    entities = db.query(Entity).order_by(Entity.entity_id.asc()).all()

    entity_ids_by_room: dict[str, list[str]] = {area.id: [] for area in areas}
    for entity in entities:
        entity_ids_by_room.setdefault(entity.room, []).append(entity.entity_id)

    return [
        {
            "id": area.id,
            "name_ru": area.name_ru,
            "entities": entity_ids_by_room.get(area.id, []),
        }
        for area in areas
    ]
