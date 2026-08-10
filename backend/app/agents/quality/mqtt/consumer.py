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
    _INITIAL_BACKOFF = 5
    _MAX_BACKOFF = 60

    def __init__(self, broker_url="127.0.0.1", port=1883):
        self.broker_url = broker_url
        self.port = port
        self.rules = QualityEngine()
        self._running = False
        self._backoff = self._INITIAL_BACKOFF
        self._consecutive_failures = 0
        
    async def run(self):
        self._running = True
        logger.info(f"MQTT Consumer started on {self.broker_url}:{self.port}")
        
        while self._running:
            try:
                async with aiomqtt.Client(hostname=self.broker_url, port=self.port, identifier="fastapi_quality_agent") as client:
                    # Connection succeeded — reset backoff
                    if self._consecutive_failures > 0:
                        logger.info("Reconnected to Mosquitto successfully.")
                    self._backoff = self._INITIAL_BACKOFF
                    self._consecutive_failures = 0

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
                self._consecutive_failures += 1
                if self._consecutive_failures <= 1:
                    logger.warning(f"Connection to Mosquitto failed: {error}. Retrying in {self._backoff}s (will back off on repeated failures)...")
                else:
                    logger.debug(f"Mosquitto still unavailable (attempt {self._consecutive_failures}). Next retry in {self._backoff}s.")
                await asyncio.sleep(self._backoff)
                self._backoff = min(self._backoff * 2, self._MAX_BACKOFF)
            except Exception as e:
                logger.error(f"MQTT Consumer fatally crashed: {e}")
                await asyncio.sleep(self._INITIAL_BACKOFF)

    async def _process_message(self, raw_payload: dict):
        dto = MQTTMachineTelemetry(**raw_payload)
        m_id = dto.machine_id
        
        async with get_sessionmaker()() as session:
            # 1. Store precise sensor history 
            json_dump = dto.model_dump(mode='json')
            dumped = dto.model_dump()
            db_sensor = SensorHistory(**dumped)
            session.add(db_sensor)

            # 2. Evaluate Deterministic Risk Engine 
            status_dto = self.rules.evaluate(dto)

            # 3. Upsert Stateful Metric block
            state_values = status_dto.model_dump(exclude={"issues"})
            status_obj = await session.get(MachineState, m_id)
            if not status_obj:
                status_obj = MachineState(**state_values)
                session.add(status_obj)
            else:
                for k, v in state_values.items():
                    setattr(status_obj, k, v)
                    
            # 4. Generate Internal Notification Event triggers if risk reaches limits
            if status_dto.issues:
                highest = next((issue for issue in status_dto.issues if issue.severity == "CRITICAL"), status_dto.issues[0])
                alert = QualityAlerts(
                    machine_id=m_id, 
                    severity=highest.severity,
                    message=highest.description,
                    context_data={**json_dump, "issues": [issue.model_dump() for issue in status_dto.issues], "status": "DETECTED"},
                )
                session.add(alert)
                await bus.publish("quality:alert", {"machine_id": m_id, "status": status_dto.model_dump(mode='json'), "sensor": json_dump})

            # Broadcast native WebSockets push message (Phase 8 UI refactor dependencies)
            await bus.publish(
                "quality:updated",
                {"machine_id": m_id, "status": status_dto.model_dump(mode='json'), "telemetry": json_dump}
            )

            await session.commit()
            
    async def stop(self):
        self._running = False

mqtt_consumer = MQTTConsumer()
