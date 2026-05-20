from __future__ import annotations

from typing import Dict, Union

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.ml_features import build_feature_vector
from db.models import MLHistory


router = APIRouter(
    prefix="/ml",
    tags=["ml"],
    dependencies=[Depends(get_current_user)],
)


def serialize_ml_history(record: MLHistory) -> dict[str, object]:
    return {
        "id": record.id,
        "scenario": record.scenario,
        "confidence": record.confidence,
        "probabilities": record.probabilities or {},
        "applied": bool(record.applied),
        "feature_vector": record.feature_vector or {},
        "triggered_by": record.triggered_by,
        "created_at": record.created_at.isoformat(),
    }


@router.get("/history")
def get_ml_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    total = db.query(MLHistory).count()
    items = (
        db.query(MLHistory)
        .order_by(MLHistory.created_at.desc(), MLHistory.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "items": [serialize_ml_history(item) for item in items],
        "total": total,
    }


@router.get("/current-scene")
def get_current_scene(request: Request) -> dict[str, object]:
    return {
        "scene": request.app.state.current_scene,
        "confidence": request.app.state.last_confidence,
        "last_decision_at": request.app.state.last_decision_at,
    }


@router.get("/feature-vector")
def get_feature_vector(
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, Union[int, float]]:
    return build_feature_vector(
        db,
        last_motion_at=getattr(request.app.state, "last_motion_at", None),
    )
