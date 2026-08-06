import asyncio
import asyncpg
import os

url = "postgresql://postgres.jhzvbsdxhqsfwnhhcgyy:4jxeGyjBbl6OdH1Q@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"

async def run():
    conn = await asyncpg.connect(url)
    rows = await conn.fetch('SELECT email, role FROM users')
    for r in rows:
        print(r['email'], r['role'])
    await conn.close()

asyncio.run(run())
