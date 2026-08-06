from datetime import datetime
from app.agents.quality.schemas import SensorDataDTO, MachineStatusDTO
from app.core.logging import get_logger

logger = get_logger(__name__)

class QualityEngine:
    """Deterministic Rule Engine for manufacturing sensor data."""

    def evaluate(self, data: SensorDataDTO) -> MachineStatusDTO:
        # 1. Base Penalties
        health_penalty = 0.0
        
        # Temperature Penalty (Threshold 50)
        if data.temperature > 50:
            health_penalty += (data.temperature - 50) * 1.5
            
        # Vibration Penalty (Threshold 5.0)
        if data.vibration > 5.0:
            health_penalty += (data.vibration - 5.0) * 5.0
            
        # Tool Wear (Threshold 60%)
        if data.tool_wear > 60:
            health_penalty += (data.tool_wear - 60) * 0.5
            
        # 2. Final Health
        health_score = max(0.0, min(100.0, 100.0 - health_penalty))
        
        # 3. Quality Score
        if data.product_count > 0:
            quality_score = max(0.0, ((data.product_count - data.defect_count) / data.product_count) * 100.0)
        else:
            quality_score = 100.0
            
        # 4. Risk Level
        if health_score < 40 or quality_score < 70:
            risk_level = "HIGH"
        elif health_score < 75 or quality_score < 90:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            
        # 5. Inspection Requirements
        if risk_level == "HIGH":
            inspection_result = "FAIL - IMMEDIATE MAINTENANCE"
        elif risk_level == "MEDIUM":
            inspection_result = "WARNING - SCHEDULE REVIEW"
        else:
            inspection_result = "PASS"
            
        return MachineStatusDTO(
            machine_id=data.machine_id,
            health_score=round(health_score, 1),
            quality_score=round(quality_score, 1),
            risk_level=risk_level,
            inspection_result=inspection_result,
            last_updated=datetime.utcnow()
        )
