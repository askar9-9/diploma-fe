from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Area(Base):
    __tablename__ = "areas"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name_ru: Mapped[str] = mapped_column(String, nullable=False)

    entities: Mapped[list["Entity"]] = relationship(
        "Entity",
        back_populates="area",
        cascade="all, delete-orphan",
    )


class Entity(Base):
    __tablename__ = "entities"

    entity_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False, default="")
    domain: Mapped[str] = mapped_column(String, nullable=False)
    room: Mapped[str] = mapped_column(ForeignKey("areas.id"), nullable=False)
    room_ru: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False, default="off")
    attributes: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    doc_url: Mapped[str] = mapped_column(String, nullable=False, default="")
    power_kw: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    area: Mapped["Area"] = relationship("Area", back_populates="entities")


class EnergyReading(Base):
    __tablename__ = "energy_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String, nullable=False)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    total_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )


class MLHistory(Base):
    __tablename__ = "ml_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scenario: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    probabilities: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    applied: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    feature_vector: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    triggered_by: Mapped[str] = mapped_column(String, nullable=False, default="auto")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )


class DeviceState(Base):
    __tablename__ = "device_states"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    device_type: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
