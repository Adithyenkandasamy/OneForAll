import asyncio
from app.database.session import get_sessionmaker
from app.agents.quality.models import MachineStatus
from sqlalchemy import select

async def get():
    async with get_sessionmaker()() as session:
        r = await session.execute(select(MachineStatus))
        ms = r.scalars().all()
        print([m.machine_id for m in ms])

asyncio.run(get())
