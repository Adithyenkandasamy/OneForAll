import asyncio
import json
import aiomqtt
from datetime import datetime, timezone
from app.core.logging import get_logger
from app.database.session import get_sessionmaker
from app.agents.quality.schemas import MQTTMachineTelemetry
from app.agents.quality.models import SensorHistory, MachineState, QualityAlerts
from app.agents.quality.rules.quality_engine import QualityEngine
from app.shared.events import bus

logger = get_logger(__name__)

class MQTTConsumer:
    def __init__(self, broker_url="127.0.0.1", port=1883):
        self.broker_url = broker_url
        self.port = port
        self.rules = QualityEngine()
        self._running = False
        
    async def run(self):
        self._running = True
        logger.info(f"MQTT Consumer started on {self.broker_url}:{self.port}")
        
        while self._running:
            try:
                async with aiomqtt.Client(hostname=self.broker_url, port=self.port, identifier="fastapi_quality_agent") as client:
                    await client.subscribe("factory/machines/#")
                    async for message in client.messages:
                        if not self._running:
                            break
                        try:
                            payload = json.loads(message.payload.decode())
                            await self._process_message(payload)
                        except Exception as parse_error:
                            logger.error(f"Malformed MQTT Payload on {message.topic}: {parse_error}")
            except aiomqtt.MqttError as error:
                logger.warning(f"Connection to Mosquitto dropped: {error}. Reconnecting in 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"MQTT Consumer fatally crashed: {e}")
                await asyncio.sleep(5)

    async def _process_message(self, raw_payload: dict):
        dto = MQTTMachineTelemetry(**raw_payload)
        m_id = dto.machine_id
        
        async with get_sessionmaker()() as session:
            # 1. Store precise sensor history 
            dumped = dto.model_dump()
            db_sensor = SensorHistory(**dumped)
            session.add(db_sensor)

            # 2. Evaluate Deterministic Risk Engine 
            status_dto = self.rules.evaluate(dto)

            # 3. Upsert Stateful Metric block
            status_obj = await session.get(MachineState, m_id)
            if not status_obj:
                status_obj = MachineState(**status_dto.model_dump())
                session.add(status_obj)
            else:
                for k, v in status_dto.model_dump().items():
                    setattr(status_obj, k, v)
                    
            # 4. Generate Internal Notification Event triggers if risk reaches limits
            if status_dto.risk_level == "HIGH":
                alert = QualityAlerts(
                    machine_id=m_id, 
                    severity="CRITICAL", 
                    message=f"Risk Level CRITICAL detected. Metric Inspection: {status_dto.inspection_result}",
                    context_data=dumped
                )
                session.add(alert)
                await bus.publish("quality:alert", {"machine_id": m_id, "status": status_dto.model_dump(), "sensor": dumped})

            # Broadcast native WebSockets push message (Phase 8 UI refactor dependencies)
            await bus.publish(
                "quality:updated",
                {"machine_id": m_id, "status": status_dto.model_dump(), "telemetry": dumped}
            )

            await session.commit()
            
    async def stop(self):
        self._running = False

mqtt_consumer = MQTTConsumer()
