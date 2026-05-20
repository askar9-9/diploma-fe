from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.db import get_db
from db.models import EnergyReading


router = APIRouter(
    prefix="/energy",
    tags=["energy"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/history")
def get_energy_history(db: Session = Depends(get_db)) -> dict[str, list[dict[str, object]]]:
    rows = (
        db.query(
            EnergyReading.date.label("date"),
            func.sum(EnergyReading.total_kwh).label("total_kwh"),
        )
        .group_by(EnergyReading.date)
        .order_by(EnergyReading.date.desc())
        .limit(7)
        .all()
    )

    days = [
        {"date": row.date, "total_kwh": float(row.total_kwh)}
        for row in reversed(rows)
    ]
    return {"days": days}
