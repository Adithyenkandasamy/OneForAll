"""AI history routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import ORMModel
from app.services.history_service import HistoryService


class AIHistoryRead(ORMModel):
    id: str
    agent_name: str
    query: str
    response: str
    model: str
    tool_calls_used: int
    risk_flags: list | None
    created_at: object


router = APIRouter(prefix="/history", tags=["history"])


def _get_history_service(session: DbSession) -> HistoryService:
    from app.core.container import get_container

    return get_container().history_service(session)


@router.get("", response_model=list[AIHistoryRead])
async def list_history(
    current_user: CurrentUser,
    agent_name: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: HistoryService = Depends(_get_history_service),
) -> object:
    return await service.list_for_user(
        current_user.id, agent_name=agent_name, limit=limit, offset=offset
    )
