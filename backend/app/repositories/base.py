"""Generic async repository base.

Repositories are the only component that touches the database. Services
depend on repository instances injected via the container, which keeps the
persistence technology swappable (SQLAlchemy today, another adapter later).
"""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, entity_id: str) -> T | None:
        return await self._session.get(self._entity_type(), entity_id)

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[T]:
        stmt = select(self._entity_type()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self._entity_type())
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def add(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def update(self, entity: T) -> T:
        await self._session.flush()
        return entity

    async def delete(self, entity: T) -> None:
        await self._session.delete(entity)
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()

    def _entity_type(self) -> type[T]:
        return self.__orig_bases__[0].__args__[0]
