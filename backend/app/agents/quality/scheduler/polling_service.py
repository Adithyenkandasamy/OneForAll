import asyncio
import httpx
from datetime import datetime
from app.core.logging import get_logger
from app.database.core import async_session_maker
from app.agents.quality.schemas import SensorDataDTO
from app.agents.quality.models import SensorData, MachineStatus
from app.agents.quality.rules.quality_engine import QualityEngine
from app.shared.events import bus

logger = get_logger(__name__)

MOCKAROO_URL = "https://my.api.mockaroo.com/manufacturing_quality_data.json?key=0357c980"

class QualityPollingService:
    def __init__(self, interval_seconds: int = 10):
        self.interval = interval_seconds
        self.rules = QualityEngine()
        self._running = False
        
    async def run(self):
        self._running = True
        logger.info("Quality Polling Service started.")
        async with httpx.AsyncClient() as client:
            while self._running:
                try:
                    await self._cycle(client)
                except Exception as e:
                    logger.error(f"Polling cycle failed: {e}")
                await asyncio.sleep(self.interval)

    async def stop(self):
        self._running = False
        
    async def _cycle(self, client: httpx.AsyncClient):
        # 1. Fetch Mockaroo Telemetry
        resp = await client.get(MOCKAROO_URL, timeout=10.0)
        resp.raise_for_status()
        raw_rows = resp.json()
        
        async with async_session_maker() as session:
            for row in raw_rows:
                # Convert basic integer IDs from the mock into arbitrary machine clusters
                # (E.g. id: 1 -> Machine-01)
                m_id = f"Machine-{str(row['id']).zfill(2)}"
                row["machine_id"] = m_id
                
                dto = SensorDataDTO(**row)
                
                # 2. Persist Sensor Data History
                db_sensor = SensorData(**dto.model_dump())
                session.add(db_sensor)
                
                # 3. Deterministic Evaluation
                status_dto = self.rules.evaluate(dto)
                
                # 4. Upsert Machine Status
                status_obj = await session.get(MachineStatus, m_id)
                if not status_obj:
                    status_obj = MachineStatus(**status_dto.model_dump())
                    session.add(status_obj)
                else:
                    status_dict = status_dto.model_dump()
                    for k, v in status_dict.items():
                        setattr(status_obj, k, v)
                
                # 5. Broadcast alerts if HIGH risk
                if status_dto.risk_level == "HIGH":
                    await bus.publish(
                        "quality:alert", 
                        {"machine_id": m_id, "status": status_dto.model_dump(), "sensor": dto.model_dump()}
                    )
                    
                # Broadcast generic update to WebSocket channels
                await bus.publish(
                    "quality:update",
                    {"machine_id": m_id, "status": status_dto.model_dump()}
                )
                
            await session.commit()
        logger.debug(f"Polled {len(raw_rows)} telemetry frames successfully.")

# Singleton instance
polling_service = QualityPollingService()
