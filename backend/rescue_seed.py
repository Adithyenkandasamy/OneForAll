import asyncio
from app.database.session import get_sessionmaker
from app.models.user import User
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed():
    async with get_sessionmaker()() as session:
        # Check if admin exists
        # Add admin
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@orvixo.com",
            full_name="Adithyen K",
            password_hash=pwd_context.hash("admin123"),
            role="admin",
            is_active=True,
            email_verified=True
        )
        session.add(admin)
        await session.commit()
        print("Restored admin account: admin@orvixo.com / admin123")

if __name__ == "__main__":
    asyncio.run(seed())
