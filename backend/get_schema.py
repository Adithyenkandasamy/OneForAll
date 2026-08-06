import asyncio
import asyncpg

url = "postgresql://postgres.jhzvbsdxhqsfwnhhcgyy:4jxeGyjBbl6OdH1Q@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"

async def run():
    conn = await asyncpg.connect(url)
    cols = await conn.fetch("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'")
    print([c['column_name'] for c in cols])
    await conn.close()

asyncio.run(run())
