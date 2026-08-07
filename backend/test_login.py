import asyncio
from app.database.session import get_sessionmaker
from app.models.user import User
from app.core.security import verify_password
from sqlalchemy import select

async def test_auth():
    async with get_sessionmaker()() as session:
        result = await session.execute(select(User).where(User.email == "adithyen1@gmail.com"))
        user = result.scalars().first()
        if user:
            print("Found user:", user.email)
            print("Hash:", user.password_hash)
            match = verify_password("adithyen123", user.password_hash)
            print("Password adithyen123 matches:", match)
        else:
            print("User not found!")

if __name__ == "__main__":
    asyncio.run(test_auth())
