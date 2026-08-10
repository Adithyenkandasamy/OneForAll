from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from app.database.session import get_sessionmaker
from app.agents.quality.models import MachineState, SensorHistory, QualityAlerts
from app.agents.quality.llm.agent import QualityAgent


class QualityService:
    def __init__(self):
        self.agent = QualityAgent()

    async def get_dashboard_state(self) -> dict:
        """Per-machine state + latest sensor reading for the frontend table."""
        async with get_sessionmaker()() as session:
            result = await session.execute(select(MachineState))
            machines = result.scalars().all()

            d_machines = []
            for m in machines:
                s_res = await session.execute(
                    select(SensorHistory)
                    .where(SensorHistory.machine_id == m.machine_id)
                    .order_by(SensorHistory.timestamp.desc())
                    .limit(1)
                )
                sensor = s_res.scalars().first()
                d_machines.append(
                    {
                        "machine_id": m.machine_id,
                        "health_score": m.health_score,
                        "quality_score": m.quality_score,
                        "risk_level": m.risk_level,
                        "inspection_result": m.inspection_result,
                        "temperature": sensor.temperature if sensor else None,
                        "vibration": sensor.vibration if sensor else None,
                        "tool_wear": sensor.tool_wear if sensor else None,
                        "rpm": sensor.rpm if sensor else None,
                        "status_time": m.last_updated.isoformat(),
                    }
                )

            return {"machines": d_machines}

    async def get_fleet_summary(self) -> dict:
        """
        High-level fleet summary for the Executive AI (RAG context).

        Returns:
          - fleet-level aggregates (avg health, avg quality, breakdown by risk)
          - list of machines needing immediate attention
          - recent alert count (last 30 min)
        """
        async with get_sessionmaker()() as session:
            result = await session.execute(select(MachineState))
            machines = result.scalars().all()

            if not machines:
                return {"error": "No machine data available yet. Start the IoT simulator."}

            total = len(machines)
            avg_health = round(sum(m.health_score for m in machines) / total, 1)
            avg_quality = round(sum(m.quality_score for m in machines) / total, 1)

            risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
            needs_attention = []
            for m in machines:
                lvl = m.risk_level.upper()
                risk_counts[lvl] = risk_counts.get(lvl, 0) + 1
                if lvl in ("HIGH", "CRITICAL"):
                    needs_attention.append(
                        {
                            "machine_id": m.machine_id,
                            "health_score": m.health_score,
                            "quality_score": m.quality_score,
                            "risk_level": m.risk_level,
                            "inspection_result": m.inspection_result,
                        }
                    )

            # Recent alerts in last 30 minutes
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
            alert_res = await session.execute(
                select(func.count()).select_from(QualityAlerts).where(QualityAlerts.created_at >= cutoff)
            )
            recent_alert_count = alert_res.scalar() or 0

            return {
                "fleet_size": total,
                "avg_health_score": avg_health,
                "avg_quality_score": avg_quality,
                "risk_distribution": risk_counts,
                "machines_needing_attention": needs_attention,
                "recent_alerts_30min": recent_alert_count,
                "operational_status": (
                    "CRITICAL" if risk_counts.get("CRITICAL", 0) > 0
                    else "DEGRADED" if risk_counts.get("HIGH", 0) > 0
                    else "CAUTION" if risk_counts.get("MEDIUM", 0) > 2
                    else "NOMINAL"
                ),
            }

    async def get_recent_alerts(self, limit: int = 20) -> dict:
        """Return the most recent quality alerts for the Executive AI."""
        async with get_sessionmaker()() as session:
            res = await session.execute(
                select(QualityAlerts)
                .order_by(QualityAlerts.created_at.desc())
                .limit(limit)
            )
            alerts = res.scalars().all()
            return {
                "alerts": [
                    {
                        "machine_id": a.machine_id,
                        "severity": a.severity,
                        "message": a.message,
                        "created_at": a.created_at.isoformat(),
                        "resolved": a.resolved_at is not None,
                    }
                    for a in alerts
                ],
                "total_returned": len(alerts),
            }

    async def get_machine_telemetry(self, machine_id: str, limit: int = 10) -> dict:
        """Return recent sensor history for a specific machine — enables per-machine RAG."""
        async with get_sessionmaker()() as session:
            res = await session.execute(
                select(SensorHistory)
                .where(SensorHistory.machine_id == machine_id.upper())
                .order_by(SensorHistory.timestamp.desc())
                .limit(limit)
            )
            readings = res.scalars().all()

            if not readings:
                return {"error": f"No telemetry found for machine {machine_id}. Check machine_id."}

            return {
                "machine_id": machine_id.upper(),
                "readings": [
                    {
                        "timestamp": r.timestamp.isoformat(),
                        "temperature": r.temperature,
                        "vibration": r.vibration,
                        "rpm": r.rpm,
                        "tool_wear": r.tool_wear,
                        "power": r.power,
                        "product_count": r.product_count,
                        "defect_count": r.defect_count,
                    }
                    for r in readings
                ],
            }

    async def answer(self, prompt: str) -> dict:
        state = await self.get_dashboard_state()
        answer = await self.agent.chat(prompt, state)
        return {"role": "assistant", "content": answer}
