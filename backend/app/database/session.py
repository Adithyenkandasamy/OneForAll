"""Async SQLAlchemy engine and session factory.

The engine is created lazily so importing ``app.main`` does not require a
live database. Tests override ``DATABASE_URL`` with ``sqlite+aiosqlite``.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def _get_engine() -> AsyncEngine:
    global _engine, _sessionmaker
    if _engine is None:
        url = settings.db_dsn
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        _engine = create_async_engine(url, connect_args=connect_args, pool_pre_ping=True)
        _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    _get_engine()
    assert _sessionmaker is not None
    return _sessionmaker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Request-scoped session. Commits on success, rolls back on error."""
    async with get_sessionmaker()() as session:
        try:
            yield session
            await session.commit()
        except BaseException:
            await session.rollback()
            raise


async def init_db() -> None:
    """Create tables from ORM models (dev convenience; prod uses migrations)."""
    from app import models  # noqa: F401
    from app.database import base  # noqa: F401  (imports all models)

    async with _get_engine().begin() as conn:
        await conn.run_sync(base.Base.metadata.create_all)
