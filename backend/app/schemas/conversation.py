"""Conversation DTOs."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ConversationCreate(BaseModel):
    agent_name: str = Field(default="inventory", pattern=r"^[a-z_]+$")
    title: str = Field(default="", max_length=255)


class ConversationRead(ORMModel):
    id: str
    agent_name: str
    title: str
    created_at: datetime
    updated_at: datetime


class MessageRead(ORMModel):
    id: str
    role: str
    content: str
    tool_calls: list | None
    created_at: datetime


class MessageSend(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
