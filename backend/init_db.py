import asyncio
from app.database.session import _engine
from app.database.base import Base
from app.agents.quality.models import SensorData, MachineStatus

async def init_db():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created!")

if __name__ == "__main__":
    asyncio.run(init_db())
