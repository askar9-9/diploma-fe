from __future__ import annotations

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.ml_features import build_feature_vector
from db.models import MLHistory


router = APIRouter(
    prefix="/scenes",
    tags=["scenes"],
    dependencies=[Depends(get_current_user)],
)


class ActivateSceneRequest(BaseModel):
    scene: Literal["day", "night", "away", "movie"]


@router.post("/activate")
async def activate_scene(
    payload: ActivateSceneRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    request.app.state.mqtt_handler.publish_scene(payload.scene)

    record = MLHistory(
        scenario=payload.scene,
        confidence=1.0,
        probabilities={payload.scene: 1.0},
        applied=True,
        feature_vector=build_feature_vector(
            db,
            last_motion_at=getattr(request.app.state, "last_motion_at", None),
        ),
        triggered_by="manual",
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    request.app.state.current_scene = payload.scene
    request.app.state.last_confidence = 1.0
    request.app.state.last_decision_at = record.created_at.isoformat()

    await request.app.state.ws_manager.broadcast(
        {
            "type": "scene_changed",
            "scene": payload.scene,
            "confidence": 1.0,
            "triggered_by": "manual",
        }
    )
    return {"status": "ok", "scene": payload.scene}
