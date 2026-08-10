from datetime import datetime, timezone
from app.agents.quality.schemas import MQTTMachineTelemetry, MonitoringIssue, QualityAnalysisResult
from app.core.logging import get_logger

logger = get_logger(__name__)

class QualityEngine:
    """Deterministic Rule Engine for manufacturing sensor data."""

    TEMPERATURE_WARNING = 75.0
    TEMPERATURE_CRITICAL = 90.0
    VIBRATION_WARNING = 4.5
    VIBRATION_CRITICAL = 6.0
    MOTOR_LOAD_WARNING = 85.0
    MOTOR_LOAD_CRITICAL = 95.0
    TOOL_WEAR_WARNING = 70.0
    TOOL_WEAR_CRITICAL = 85.0
    COOLANT_LOW = 20.0

    @staticmethod
    def _issue(
        issue_type: str, severity: str, parameter: str, current_value: float, threshold: float, description: str
    ) -> MonitoringIssue:
        return MonitoringIssue(
            issue_type=issue_type,
            severity=severity,
            parameter=parameter,
            current_value=round(current_value, 2),
            threshold=threshold,
            description=description,
        )

    def evaluate(self, data: MQTTMachineTelemetry) -> QualityAnalysisResult:
        issues: list[MonitoringIssue] = []

        if data.temperature > self.TEMPERATURE_CRITICAL:
            issues.append(self._issue("CRITICAL_TEMPERATURE", "CRITICAL", "temperature", data.temperature, self.TEMPERATURE_CRITICAL, "Temperature exceeds the critical operating limit."))
        elif data.temperature > self.TEMPERATURE_WARNING:
            issues.append(self._issue("HIGH_TEMPERATURE", "HIGH", "temperature", data.temperature, self.TEMPERATURE_WARNING, "Temperature exceeds the warning operating limit."))
        if data.vibration > self.VIBRATION_CRITICAL:
            issues.append(self._issue("CRITICAL_VIBRATION", "CRITICAL", "vibration", data.vibration, self.VIBRATION_CRITICAL, "Vibration exceeds the critical operating limit."))
        elif data.vibration > self.VIBRATION_WARNING:
            issues.append(self._issue("HIGH_VIBRATION", "HIGH", "vibration", data.vibration, self.VIBRATION_WARNING, "Vibration exceeds the warning operating limit."))
        if data.motor_load is not None and data.motor_load > self.MOTOR_LOAD_CRITICAL:
            issues.append(self._issue("CRITICAL_MOTOR_LOAD", "CRITICAL", "motor_load", data.motor_load, self.MOTOR_LOAD_CRITICAL, "Motor load is critically high."))
        elif data.motor_load is not None and data.motor_load > self.MOTOR_LOAD_WARNING:
            issues.append(self._issue("HIGH_MOTOR_LOAD", "HIGH", "motor_load", data.motor_load, self.MOTOR_LOAD_WARNING, "Motor load exceeds the warning limit."))
        if data.tool_wear > self.TOOL_WEAR_CRITICAL:
            issues.append(self._issue("CRITICAL_TOOL_WEAR", "CRITICAL", "tool_wear", data.tool_wear, self.TOOL_WEAR_CRITICAL, "Tool wear requires immediate maintenance."))
        elif data.tool_wear > self.TOOL_WEAR_WARNING:
            issues.append(self._issue("HIGH_TOOL_WEAR", "HIGH", "tool_wear", data.tool_wear, self.TOOL_WEAR_WARNING, "Tool wear exceeds the warning limit."))
        if data.coolant_level is not None and data.coolant_level < self.COOLANT_LOW:
            issues.append(self._issue("LOW_COOLANT", "HIGH", "coolant_level", data.coolant_level, self.COOLANT_LOW, "Coolant level is below the safe limit."))

        if sum(issue.severity in {"HIGH", "CRITICAL"} for issue in issues) >= 2:
            issues.append(self._issue("POSSIBLE_MECHANICAL_STRESS", "CRITICAL", "combined", 2, 2, "Multiple elevated machine signals indicate possible mechanical stress."))

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
        if any(issue.severity == "CRITICAL" for issue in issues) or health_score < 40 or quality_score < 70:
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
            
        return QualityAnalysisResult(
            machine_id=data.machine_id,
            health_score=round(health_score, 1),
            quality_score=round(quality_score, 1),
            risk_level=risk_level,
            inspection_result=inspection_result,
            issues=issues,
            last_updated=datetime.now(timezone.utc)
        )
