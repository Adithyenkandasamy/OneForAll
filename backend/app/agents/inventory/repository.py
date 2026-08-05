"""Inventory agent persistence adapter.

Bridges the agent's ``HistorySink`` port to the platform's history service
through duck typing, so this package never imports app-layer modules.
The composition root supplies a recorder exposing ``record(**record)``.
"""

from __future__ import annotations

from typing import Any


class HistorySinkAdapter:
    """Adapts any ``record(**kwargs) -> None`` recorder to HistorySink."""

    def __init__(self, recorder: Any) -> None:
        self._recorder = recorder

    async def save(self, record: dict[str, Any]) -> None:
        await self._recorder.record(**record)
