"""AI history use-cases. Stores ONLY platform-owned AI analysis records."""

from __future__ import annotations

from datetime import datetime, timezone

from app.core.exceptions import NotFoundError
from app.models.ai_history import AIHistory
from app.repositories.history_repository import HistoryRepository
from app.utils.ids import new_id


class HistoryService:
    def __init__(self, history: HistoryRepository) -> None:
        self._history = history

    async def record(
        self,
        *,
        user_id: str,
        agent_name: str,
        query: str,
        response: str,
        model: str,
        tool_calls_used: int = 0,
        risk_flags: list | None = None,
    ) -> AIHistory:
        now = datetime.now(timezone.utc)
        return await self._history.add(
            AIHistory(
                id=new_id(),
                user_id=user_id,
                agent_name=agent_name,
                query=query,
                response=response,
                model=model,
                tool_calls_used=tool_calls_used,
                risk_flags=risk_flags,
                started_at=now,
                completed_at=now,
            )
        )

    async def list_for_user(
        self, user_id: str, *, agent_name: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[AIHistory]:
        return await self._history.list_for_user(
            user_id, agent_name=agent_name, limit=limit, offset=offset
        )

    async def get(self, history_id: str) -> AIHistory:
        history = await self._history.get(history_id)
        if history is None:
            raise NotFoundError("History record not found")
        return history
