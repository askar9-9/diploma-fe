from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from db.models import Event


router = APIRouter(
    prefix="/events",
    tags=["events"],
    dependencies=[Depends(get_current_user)],
)


def _serialize_event(event: Event) -> dict[str, object]:
    device_name = event.device.name if event.device else event.device_id
    return {
        "id": event.id,
        "device_id": event.device_id,
        "device_name": device_name,
        "new_state": event.new_state,
        "created_at": event.created_at.isoformat(),
    }


@router.get("")
def list_events(
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[dict[str, object]]:
    records = (
        db.query(Event)
        .order_by(Event.created_at.desc())
        .limit(limit)
        .all()
    )
    return [_serialize_event(event) for event in records]
