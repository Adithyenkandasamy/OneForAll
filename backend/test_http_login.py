import asyncio
import httpx

async def run():
    async with httpx.AsyncClient() as client:
        res = await client.post("http://127.0.0.1:8000/api/v1/auth/login", json={
            "email": "adithyen1@gmail.com",
            "password": "adithyen123"
        })
        print(res.status_code, res.text)

if __name__ == "__main__":
    asyncio.run(run())
