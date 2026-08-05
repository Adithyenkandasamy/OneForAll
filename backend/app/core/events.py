"""Domain event definitions.

Agents publish events (e.g. ``InventoryAnalysisCompleted``) to the in-process
event bus in ``app/shared/messaging/event_bus.py``. Services subscribe. When a
queue transport replaces the bus during microservice migration, these payloads
are unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class DomainEvent:
    event_type: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    actor_id: str | None = None


@dataclass(frozen=True)
class InventoryAnalysisCompleted(DomainEvent):
    conversation_id: str | None = None
    summary: str | None = None
    low_stock_count: int = 0


@dataclass(frozen=True)
class InventoryRiskDetected(DomainEvent):
    skus: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class InventoryUpdated(DomainEvent):
    sku: str | None = None
    column: str | None = None
    value: str | None = None
