import asyncio
from app.database.core import engine, Base
# Import all models to register them with Base.metadata
from app.agents.quality.models import SensorData, MachineStatus

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created!")

if __name__ == "__main__":
    asyncio.run(init_db())
