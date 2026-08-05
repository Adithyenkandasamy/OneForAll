"""Notification DTOs."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class NotificationRead(ORMModel):
    id: str
    kind: str
    title: str
    body: str
    is_read: bool
    created_at: datetime


class NotificationMarkRead(BaseModel):
    ids: list[str]
