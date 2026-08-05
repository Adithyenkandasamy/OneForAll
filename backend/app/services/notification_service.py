"""Notification use-cases."""

from __future__ import annotations

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.utils.ids import new_id


class NotificationService:
    def __init__(self, notifications: NotificationRepository) -> None:
        self._notifications = notifications

    async def create(
        self, *, user_id: str, kind: str, title: str, body: str = "", payload: dict | None = None
    ) -> Notification:
        return await self._notifications.add(
            Notification(
                id=new_id(), user_id=user_id, kind=kind, title=title, body=body, payload=payload
            )
        )

    async def list_for_user(
        self, user_id: str, *, unread_only: bool = False, limit: int = 50, offset: int = 0
    ) -> list[Notification]:
        return await self._notifications.list_for_user(
            user_id, unread_only=unread_only, limit=limit, offset=offset
        )

    async def mark_read(self, user_id: str, notification_ids: list[str]) -> int:
        count = 0
        for notification_id in notification_ids:
            notification = await self._notifications.get(notification_id)
            if notification is None or notification.user_id != user_id:
                continue
            notification.is_read = True
            count += 1
        return count

    async def count_unread(self, user_id: str) -> int:
        return await self._notifications.count_unread(user_id)
