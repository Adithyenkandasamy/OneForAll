import asyncio
from sqlalchemy import text
from app.database.session import get_sessionmaker

async def main():
    print("STARTING HANG TEST", flush=True)
    async def try_query():
        async with get_sessionmaker()() as session:
            r = await session.execute(text("SELECT 1;"))
            print(r.scalar(), flush=True)
            
    try:
        await asyncio.wait_for(try_query(), timeout=3.0)
        print("SUCCESS", flush=True)
    except asyncio.TimeoutError:
        print("HANG DETECTED! TIMED OUT", flush=True)

asyncio.run(main())
