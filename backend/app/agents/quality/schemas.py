from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

class MQTTMachineTelemetry(BaseModel):
    machine_id: str
    temperature: float
    rpm: int
    pressure: float
    vibration: float
    humidity: int
    tool_wear: float
    power: float
    noise: int
    product_count: int
    defect_count: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QualityAnalysisResult(BaseModel):
    machine_id: str
    health_score: float
    quality_score: float
    risk_level: str
    inspection_result: str
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
