from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    device_type: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    events: Mapped[List["Event"]] = relationship("Event", back_populates="device")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String, ForeignKey("devices.id"), nullable=False)
    new_state: Mapped[float] = mapped_column(Float, nullable=False)
    attributes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    device: Mapped["Device"] = relationship("Device", back_populates="events")


class FeatureVector(Base):
    __tablename__ = "feature_vectors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hour_of_day: Mapped[int] = mapped_column(Integer, nullable=False)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    motion_hall: Mapped[int] = mapped_column(Integer, nullable=False)
    motion_living: Mapped[int] = mapped_column(Integer, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    light_level: Mapped[float] = mapped_column(Float, nullable=False)
    tv_on: Mapped[int] = mapped_column(Integer, nullable=False)
    minutes_idle: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_scenario: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    decision_source: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    commands: Mapped[str] = mapped_column(String, nullable=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class SuggestedPattern(Base):
    __tablename__ = "suggested_patterns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cluster_id: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    occurrence_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    discovered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
