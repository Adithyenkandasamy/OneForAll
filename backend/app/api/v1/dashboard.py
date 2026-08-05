"""Dashboard summary route."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, DbSession
from app.services.history_service import HistoryService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _get_notification_service(session: DbSession) -> NotificationService:
    from app.core.container import get_container

    return get_container().notification_service(session)


def _get_history_service(session: DbSession) -> HistoryService:
    from app.core.container import get_container

    return get_container().history_service(session)


@router.get("/summary")
async def dashboard_summary(
    current_user: CurrentUser,
    notification_service: NotificationService = Depends(_get_notification_service),
    history_service: HistoryService = Depends(_get_history_service),
) -> dict[str, object]:
    recent = await history_service.list_for_user(current_user.id, limit=5)
    unread = await notification_service.count_unread(current_user.id)
    return {"unread_notifications": unread, "recent_analyses": len(recent)}
