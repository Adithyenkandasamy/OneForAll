"""In-process event bus.

Agents publish domain events; services subscribe. The interface is the
seam for the microservice split: swap this transport for a message queue
(RabbitMQ/Kafka/Redis) without changing publishers or subscribers.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

from app.core.events import DomainEvent
from app.core.logging import get_logger

logger = get_logger(__name__)

Handler = Callable[[Any], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(event.event_type, []):
            try:
                await handler(event)
            except Exception as exc:  # subscribers must not break the publisher
                logger.warning(
                    "Event handler failed", extra={"handler": handler.__name__, "error": str(exc)}
                )


event_bus = EventBus()
