"""AI analysis history: one row per completed agent run."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, IdMixin, TimestampMixin


class AIHistory(Base, IdMixin, TimestampMixin):
    __tablename__ = "ai_history"

    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    agent_name: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    tool_calls_used: Mapped[int] = mapped_column(default=0, nullable=False)
    risk_flags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
