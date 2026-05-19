from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from db.models import FeatureVector


router = APIRouter(
    prefix="/ml-decisions",
    tags=["ml-decisions"],
    dependencies=[Depends(get_current_user)],
)


def _serialize_fv(fv: FeatureVector) -> dict[str, object]:
    return {
        "id": fv.id,
        "hour_of_day": fv.hour_of_day,
        "weekday": fv.weekday,
        "motion_hall": fv.motion_hall,
        "motion_living": fv.motion_living,
        "temperature": fv.temperature,
        "light_level": fv.light_level,
        "tv_on": fv.tv_on,
        "minutes_idle": fv.minutes_idle,
        "predicted_scenario": fv.predicted_scenario,
        "confidence": fv.confidence,
        "decision_source": fv.decision_source,
        "created_at": fv.created_at.isoformat(),
    }


@router.get("")
def list_ml_decisions(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[dict[str, object]]:
    records = (
        db.query(FeatureVector)
        .order_by(FeatureVector.created_at.desc())
        .limit(limit)
        .all()
    )
    return [_serialize_fv(fv) for fv in records]


@router.get("/latest")
def get_latest_ml_decision(
    db: Session = Depends(get_db),
) -> dict[str, object]:
    fv = (
        db.query(FeatureVector)
        .order_by(FeatureVector.created_at.desc())
        .first()
    )
    if fv is None:
        return {}
    return _serialize_fv(fv)
