"""Inventory Notification Service — domain-event-driven alerts.

The Inventory AI agent NEVER sends notifications directly.
Instead, the service layer emits domain events here, and this service
routes them to the platform-level NotificationService.
"""

from __future__ import annotations

from typing import Any

from app.agents.inventory.services.rule_engine import MaterialAnalysis
from app.core.logging import get_logger

logger = get_logger(__name__)


class InventoryNotificationService:
    """Bridges inventory domain events to the platform notification system."""

    def __init__(self, platform_notifier: Any = None) -> None:
        self._notifier = platform_notifier

    async def check_and_notify(
        self, analyses: list[MaterialAnalysis], *, user_id: str
    ) -> list[dict]:
        """Inspect rule engine output and emit notifications for critical events."""
        events: list[dict] = []

        for a in analyses:
            if a.stockout_detected:
                events.append({
                    "type": "STOCKOUT",
                    "severity": "critical",
                    "title": f"Stockout Alert: {a.name}",
                    "message": f"{a.name} ({a.sku}) has reached zero stock. Immediate action required.",
                    "sku": a.sku,
                })
            elif a.priority == "CRITICAL":
                events.append({
                    "type": "CRITICAL_LOW",
                    "severity": "high",
                    "title": f"Critical Stock: {a.name}",
                    "message": (
                        f"{a.name} ({a.sku}) has only {a.days_remaining} days of stock remaining. "
                        f"Current: {a.current_stock}, Minimum: {a.minimum_stock}."
                    ),
                    "sku": a.sku,
                })
            elif a.reorder_required:
                events.append({
                    "type": "REORDER",
                    "severity": "medium",
                    "title": f"Reorder Required: {a.name}",
                    "message": (
                        f"{a.name} ({a.sku}) stock is at {a.current_stock}, "
                        f"below minimum of {a.minimum_stock}."
                    ),
                    "sku": a.sku,
                })

        # Persist via platform notification service if available
        if self._notifier and events:
            for event in events:
                try:
                    await self._notifier.create(
                        user_id=user_id,
                        title=event["title"],
                        body=event["message"],
                        level=event["severity"],
                    )
                except Exception as exc:
                    logger.warning(
                        "Failed to persist notification",
                        extra={"event": event["type"], "error": str(exc)},
                    )

        return events
