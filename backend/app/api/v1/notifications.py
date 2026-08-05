"""Notification routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.notification import NotificationMarkRead, NotificationRead
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _get_notification_service(session: DbSession) -> NotificationService:
    from app.core.container import get_container

    return get_container().notification_service(session)


@router.get("", response_model=list[NotificationRead])
async def list_notifications(
    current_user: CurrentUser,
    unread_only: bool = Query(default=False),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: NotificationService = Depends(_get_notification_service),
) -> object:
    return await service.list_for_user(
        current_user.id, unread_only=unread_only, limit=limit, offset=offset
    )


@router.post("/read", response_model=dict[str, int])
async def mark_read(
    payload: NotificationMarkRead,
    current_user: CurrentUser,
    service: NotificationService = Depends(_get_notification_service),
) -> dict[str, int]:
    return {"updated": await service.mark_read(current_user.id, payload.ids)}
