"""AI history repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_history import AIHistory
from app.repositories.base import BaseRepository


class HistoryRepository(BaseRepository[AIHistory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_for_user(
        self, user_id: str, *, agent_name: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[AIHistory]:
        stmt = select(AIHistory).where(AIHistory.user_id == user_id)
        if agent_name:
            stmt = stmt.where(AIHistory.agent_name == agent_name)
        stmt = stmt.order_by(AIHistory.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
