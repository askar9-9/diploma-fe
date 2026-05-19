import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from db.models import Scenario


router = APIRouter(
    prefix="/scenarios",
    tags=["scenarios"],
    dependencies=[Depends(get_current_user)],
)


class ScenarioCreateRequest(BaseModel):
    id: str
    display_name: str
    commands: dict[str, Any]


def _serialize_scenario(scenario: Scenario) -> dict[str, Any]:
    return {
        "id": scenario.id,
        "display_name": scenario.display_name,
        "commands": json.loads(scenario.commands),
        "is_custom": scenario.is_custom,
        "created_at": scenario.created_at.isoformat(),
    }


@router.get("")
def list_scenarios(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    scenarios = db.query(Scenario).order_by(Scenario.id.asc()).all()
    return [_serialize_scenario(scenario) for scenario in scenarios]


@router.post("/{scenario_id}/activate")
def activate_scenario(
    scenario_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    request.app.state.mqtt_handler.publish_scene_activate(scenario_id)
    return {"status": "queued", "scene": scenario_id}


@router.post("")
def create_scenario(
    payload: ScenarioCreateRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    existing = db.query(Scenario).filter(Scenario.id == payload.id).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Scenario already exists",
        )

    scenario = Scenario(
        id=payload.id,
        display_name=payload.display_name,
        commands=json.dumps(payload.commands),
        is_custom=True,
        created_at=datetime.utcnow(),
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return _serialize_scenario(scenario)
