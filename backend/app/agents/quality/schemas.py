from pydantic import BaseModel, Field
from datetime import datetime

class MockarooSensorRead(BaseModel):
    id: int
    temperature: float
    vibration: float
    rpm: int
    pressure: float
    humidity: float
    spindle_load: float
    tool_wear: float
    power_consumption: float
    noise_level: float
    product_count: int
    defect_count: int

class SensorDataDTO(MockarooSensorRead):
    machine_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MachineStatusDTO(BaseModel):
    machine_id: str
    health_score: float
    quality_score: float
    risk_level: str
    inspection_result: str
    last_updated: datetime
