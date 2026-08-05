import asyncio
from app.database.session import get_sessionmaker, init_db
from app.models.user import User
from app.core.security import hash_password

async def main():
    await init_db()
    async with get_sessionmaker()() as session:
        from sqlalchemy import select
        stmt = select(User).where(User.email == "admin@gmail.com")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            print("Admin user already exists. Updating password and role to admin.")
            user.password_hash = hash_password("admin@123")
            user.role = "admin"
        else:
            print("Creating new admin user: admin@gmail.com")
            user = User(
                id=__import__("uuid").uuid4().hex,
                email="admin@gmail.com",
                full_name="Admin",
                password_hash=hash_password("admin@123"),
                role="admin",
                is_active=True,
                email_verified=True
            )
            session.add(user)
        
        await session.commit()
        print("Admin user created/updated successfully.")

if __name__ == "__main__":
    asyncio.run(main())
