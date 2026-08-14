"""HTTP contracts for monitoring semantic search."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MonitoringSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    limit: int = Field(default=5, ge=1, le=20)
    machine_id: str | None = None
    severity: str | None = None


class MonitoringSearchResult(BaseModel):
    event_id: str
    machine_id: str
    event_type: str
    severity: str | None = None
    content: str
    metadata: dict[str, Any] | None = None
    similarity: float


class MonitoringSearchResponse(BaseModel):
    query: str
    results: list[MonitoringSearchResult]
