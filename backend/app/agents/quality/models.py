import uuid
from datetime import datetime
from sqlalchemy import Float, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class SensorData(Base):
    __tablename__ = "sensor_data"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    machine_id: Mapped[str] = mapped_column(String(255), index=True)
    temperature: Mapped[float] = mapped_column(Float)
    vibration: Mapped[float] = mapped_column(Float)
    rpm: Mapped[int] = mapped_column(Integer)
    pressure: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float] = mapped_column(Float)
    spindle_load: Mapped[float] = mapped_column(Float)
    tool_wear: Mapped[float] = mapped_column(Float)
    power_consumption: Mapped[float] = mapped_column(Float)
    noise_level: Mapped[float] = mapped_column(Float)
    product_count: Mapped[int] = mapped_column(Integer, default=0)
    defect_count: Mapped[int] = mapped_column(Integer, default=0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class MachineStatus(Base):
    __tablename__ = "machine_status"
    
    machine_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    health_score: Mapped[float] = mapped_column(Float, default=100.0)
    quality_score: Mapped[float] = mapped_column(Float, default=100.0)
    risk_level: Mapped[str] = mapped_column(String(50), default="LOW")
    inspection_result: Mapped[str] = mapped_column(String(50), default="PASS")
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
