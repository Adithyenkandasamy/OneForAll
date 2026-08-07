import asyncio
from sqlalchemy import text
from app.database.session import get_sessionmaker

async def main():
    try:
        print("CONNECTING TO DB", flush=True)
        async with get_sessionmaker()() as session:
            r = await session.execute(text("SELECT count(*) FROM machine_status;"))
            count = r.scalar()
            print("Row Count in machine_status:", count, flush=True)
            r = await session.execute(text("SELECT * FROM machine_status;"))
            rows = r.fetchall()
            print("Rows:", rows, flush=True)
    except Exception as e:
        print("EXCEPTION:", e, flush=True)

asyncio.run(main())
