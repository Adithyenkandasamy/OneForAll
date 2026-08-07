import asyncio
from app.database.session import _get_engine
from app.database.base import Base
import app.models  # This initializes the registry

async def init_db():
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("MQTT DB Init complete.")

if __name__ == "__main__":
    asyncio.run(init_db())
