from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

def utcnow():
    return datetime.now(timezone.utc)

class Machine(Base):
    __tablename__ = "machines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    asset_type: Mapped[str] = mapped_column(String(80), default="rotating_machine")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    measurements: Mapped[list["Measurement"]] = relationship(back_populates="machine", cascade="all, delete-orphan")

class Measurement(Base):
    __tablename__ = "measurements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    product_type: Mapped[str] = mapped_column(String(1))
    air_temperature_k: Mapped[float] = mapped_column(Float)
    process_temperature_k: Mapped[float] = mapped_column(Float)
    rotational_speed_rpm: Mapped[float] = mapped_column(Float)
    torque_nm: Mapped[float] = mapped_column(Float)
    tool_wear_min: Mapped[float] = mapped_column(Float)
    machine: Mapped[Machine] = relationship(back_populates="measurements")
