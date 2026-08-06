import os
import glob

def find_replace(filepath, src, tgt):
    with open(filepath, 'r') as f:
        text = f.read()
    if src in text:
        text = text.replace(src, tgt)
        with open(filepath, 'w') as f:
            f.write(text)

find_replace("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/models.py",
             "from app.database.core import Base",
             "from app.database.base import Base")

# For polling_service
old_poll = "from app.database.core import async_session_maker"
new_poll = "from app.database.session import get_sessionmaker"
find_replace("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/scheduler/polling_service.py",
             old_poll, new_poll)
find_replace("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/scheduler/polling_service.py",
             "async_session_maker", "get_sessionmaker()")

# For service.py
find_replace("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/services/service.py",
             old_poll, new_poll)
find_replace("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/services/service.py",
             "async_session_maker", "get_sessionmaker()")


# Fix init_db.py
with open("init_db.py", "w") as f:
    f.write('''import asyncio
from app.database.session import _engine
from app.database.base import Base
from app.agents.quality.models import SensorData, MachineStatus

async def init_db():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created!")

if __name__ == "__main__":
    asyncio.run(init_db())
''')

print("Done")
