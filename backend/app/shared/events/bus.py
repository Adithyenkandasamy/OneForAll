"""Internal Async Event Bus for the Modular Monolith."""

import asyncio
from collections import defaultdict
from collections.abc import Callable, Awaitable
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class EventBus:
    """A simple in-memory asynchronous event bus."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.subscribers = defaultdict(list)
        return cls._instance

    def subscribe(self, event_name: str, handler: Callable[[Any], Awaitable[None]]):
        """Register an async handler for a specific event."""
        if handler not in self.subscribers[event_name]:
            self.subscribers[event_name].append(handler)
            logger.debug(f"Subscribed handler to event '{event_name}'")

    def unsubscribe(self, event_name: str, handler: Callable[[Any], Awaitable[None]]):
        """Remove a handler from an event."""
        if handler in self.subscribers[event_name]:
            self.subscribers[event_name].remove(handler)

    async def publish(self, event_name: str, payload: Any):
        """Fire an event asynchronously without blocking the caller."""
        handlers = self.subscribers.get(event_name, [])
        if not handlers:
            logger.debug(f"Event '{event_name}' published but has no subscribers.")
            return

        logger.info(f"Publishing event '{event_name}' to {len(handlers)} handlers.")
        # Fire and forget handlers inside asyncio tasks so the publisher isn't blocked
        for handler in handlers:
            asyncio.create_task(self._safe_execute(event_name, handler, payload))

    async def _safe_execute(self, event_name: str, handler: Callable[[Any], Awaitable[None]], payload: Any):
        try:
            await handler(payload)
        except Exception as e:
            logger.error(f"Event handler failed for event '{event_name}': {e}", exc_info=True)


# Expose a global singleton for dependency injection / generic routing
bus = EventBus()
