import asyncio
import uuid
from sqlalchemy import delete
from app.database.session import get_sessionmaker
from app.models.user import User
from app.core.security import hash_password

async def seed():
    async with get_sessionmaker()() as session:
        await session.execute(delete(User).where(User.email == "adithyen1@gmail.com"))
        user = User(
            id=str(uuid.uuid4()),
            email="adithyen1@gmail.com",
            full_name="Adithyen K",
            password_hash=hash_password("password123"),
            role="admin",
            is_active=True,
            email_verified=True
        )
        session.add(user)
        await session.commit()
if __name__ == "__main__":
    asyncio.run(seed())
