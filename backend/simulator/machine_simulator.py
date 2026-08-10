import asyncio
import random
from datetime import datetime, timezone
import json
from amqtt.broker import Broker
from amqtt.client import MQTTClient
from amqtt.mqtt.constants import QOS_1

# Define our virtual factory fleet
MACHINES = [f"CNC{str(i).zfill(2)}" for i in range(1, 11)]

# Keep track of local state physics so it isn't random
class MachinePhysics:
    def __init__(self, m_id):
        self.machine_id = m_id
        self.temperature = random.uniform(30.0, 50.0)
        self.rpm = random.randint(1200, 2000)
        self.pressure = random.uniform(90.0, 100.0)
        self.vibration = random.uniform(0.5, 2.0)
        self.humidity = random.randint(30, 50)
        self.tool_wear = random.uniform(0.0, 5.0)
        self.power = random.uniform(10.0, 15.0)
        self.noise = random.randint(60, 75)
        self.product_count = 0
        self.defect_count = 0

    def tick(self):
        # Naturally drift temperature up slowly
        self.temperature += random.uniform(0.1, 0.5)
        if self.temperature > 95:
            self.temperature -= 40 # Simulator: Operator triggered coolant

        self.tool_wear += random.uniform(0.01, 0.1)
        if self.tool_wear > 95:
            self.tool_wear = 0.0 # Simulator: Operator swapped tool

        # RPM naturally fluctuates
        self.rpm += random.randint(-50, 50)
        self.rpm = max(1000, min(3000, self.rpm))
        
        # Vibration correlates to tool wear heavily
        self.vibration = 0.5 + (self.tool_wear / 15.0) + random.uniform(-0.1, 0.2)

        # Power correlates to RPM
        self.power = (self.rpm / 100) + random.uniform(-1, 1)

        self.product_count += 1
        # Random occasionally a defect
        if random.random() > 0.95:
            self.defect_count += 1

        return {
            "machine_id": self.machine_id,
            "temperature": round(self.temperature, 2),
            "rpm": self.rpm,
            "pressure": round(self.pressure, 2),
            "vibration": round(self.vibration, 3),
            "humidity": self.humidity,
            "tool_wear": round(self.tool_wear, 2),
            "power": round(self.power, 2),
            "noise": self.noise,
            "product_count": self.product_count,
            "defect_count": self.defect_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

async def run_broker():
    config = {
        'listeners': {
            'default': {
                'type': 'tcp',
                'bind': '0.0.0.0:1883',
            },
        },
        'topic-check': {
            'enabled': False
        }
    }
    broker = Broker(config)
    await broker.start()
    return broker

async def machine_worker(m_id):
    client = MQTTClient()
    await client.connect('mqtt://127.0.0.1:1883/')
    physics = MachinePhysics(m_id)
    topic = f"factory/machines/{m_id}"
    while True:
        payload = physics.tick()
        try:
            await client.publish(topic, json.dumps(payload).encode(), qos=QOS_1)
        except BaseException as e:
            pass
        await asyncio.sleep(1.0) # 1 Hertz publishing frequency


async def main():
    broker = await run_broker()
    print("Embedded amqtt broker started on 1883", flush=True)

    # Let broker boot
    await asyncio.sleep(1)

    workers = [asyncio.create_task(machine_worker(m)) for m in MACHINES]
    print(f"Booted {len(MACHINES)} virtual machine telemetry streams.", flush=True)
    
    await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
