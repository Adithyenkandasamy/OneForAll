import asyncio
import asyncpg
import bcrypt

url = "postgresql://postgres.jhzvbsdxhqsfwnhhcgyy:4jxeGyjBbl6OdH1Q@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"

async def run():
    conn = await asyncpg.connect(url)
    hashed = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode("utf-8")
    await conn.execute("UPDATE users SET password_hash = $1 WHERE email = 'admin@gmail.com'", hashed)
    print("Password reset to admin123")
    await conn.close()

asyncio.run(run())
