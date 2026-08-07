import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class MachineState(Base):
    __tablename__ = "machine_state"
    machine_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    health_score: Mapped[float] = mapped_column(Float, default=100.0)
    quality_score: Mapped[float] = mapped_column(Float, default=100.0)
    risk_level: Mapped[str] = mapped_column(String(50), default="LOW")
    inspection_result: Mapped[str] = mapped_column(String(255), default="PASS")
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class SensorHistory(Base):
    __tablename__ = "sensor_history"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id: Mapped[str] = mapped_column(String(255), index=True)
    temperature: Mapped[float] = mapped_column(Float)
    rpm: Mapped[int] = mapped_column(Integer)
    pressure: Mapped[float] = mapped_column(Float)
    vibration: Mapped[float] = mapped_column(Float)
    humidity: Mapped[int] = mapped_column(Integer)
    tool_wear: Mapped[float] = mapped_column(Float)
    power: Mapped[float] = mapped_column(Float)
    noise: Mapped[int] = mapped_column(Integer)
    product_count: Mapped[int] = mapped_column(Integer)
    defect_count: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

class QualityAlerts(Base):
    __tablename__ = "quality_alerts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id: Mapped[str] = mapped_column(String(255), index=True)
    severity: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(String(500))
    context_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

class QualityReports(Base):
    __tablename__ = "quality_reports"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id: Mapped[str] = mapped_column(String(255), index=True)
    report_text: Mapped[str] = mapped_column(String)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class MaintenancePredictions(Base):
    __tablename__ = "maintenance_predictions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id: Mapped[str] = mapped_column(String(255), index=True)
    predicted_failure_mode: Mapped[str] = mapped_column(String(255))
    confidence_score: Mapped[float] = mapped_column(Float)
    remaining_useful_life_hours: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
