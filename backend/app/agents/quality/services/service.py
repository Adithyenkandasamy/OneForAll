from datetime import datetime
from sqlalchemy import select
from app.database.session import get_sessionmaker
from app.agents.quality.models import MachineStatus, SensorData
from app.agents.quality.llm.agent import QualityAgent

class QualityService:
    def __init__(self):
        self.agent = QualityAgent()
        
    async def get_dashboard_state(self) -> dict:
        async with get_sessionmaker()() as session:
            result = await session.execute(select(MachineStatus))
            machines = result.scalars().all()
            
            d_machines = []
            for m in machines:
                # Get latest sensor read
                s_res = await session.execute(
                    select(SensorData).where(SensorData.machine_id == m.machine_id).order_by(SensorData.timestamp.desc()).limit(1)
                )
                sensor = s_res.scalars().first()
                d_machines.append({
                    "machine_id": m.machine_id,
                    "health_score": m.health_score,
                    "quality_score": m.quality_score,
                    "risk_level": m.risk_level,
                    "inspection_result": m.inspection_result,
                    "temperature": sensor.temperature if sensor else None,
                    "vibration": sensor.vibration if sensor else None,
                    "status_time": m.last_updated.isoformat()
                })
            
            # Additional aggregate derivations
            total_defect = 0
            if machines:
               pass
               
            return {"machines": d_machines}

    async def answer(self, prompt: str) -> dict:
        # Precompute the holistic dashboard state for the Agent's causal window context
        state = await self.get_dashboard_state()
        answer = await self.agent.chat(prompt, state)
        return {"role": "asssistant", "content": answer}
