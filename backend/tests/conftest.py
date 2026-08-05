"""In-memory DB + app fixtures and dependency overrides.

No network: the DB is aiosqlite in-memory, auth is bypassed, and agent
dependencies are replaced with fakes per-test.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_user
from app.database.base import Base
from app.database.session import get_db
from app.models import *  # noqa: F401,F403  (register all models)
from app.models.user import User


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        yield session


@pytest_asyncio.fixture
async def test_app(db_session):
    from app.main import create_app

    app = create_app()

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    return app


@pytest_asyncio.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.app = test_app
        yield ac


@pytest_asyncio.fixture
def viewer_user() -> User:
    return User(
        id="user-viewer",
        email="viewer@factory.test",
        full_name="Viewer",
        password_hash="x",
        role="viewer",
        is_active=True,
    )


@pytest_asyncio.fixture
def admin_user() -> User:
    return User(
        id="user-admin",
        email="admin@factory.test",
        full_name="Admin",
        password_hash="x",
        role="admin",
        is_active=True,
    )


@pytest.fixture
def override_auth(client, viewer_user):
    async def _fake_current_user():
        return viewer_user

    client.app.dependency_overrides[get_current_user] = _fake_current_user
    return viewer_user
