"""Cache Service — TTL-based in-memory cache for MCP data.

Avoids hammering Google Sheets on every request.
The cache is invalidated on write operations.
"""

from __future__ import annotations

import time
from typing import Any


class CacheService:
    """Simple TTL cache for inventory sheet data."""

    DEFAULT_TTL_SECONDS: int = 120  # 2 minutes

    def __init__(self, ttl_seconds: int | None = None) -> None:
        self._ttl = ttl_seconds or self.DEFAULT_TTL_SECONDS
        self._data: list[dict[str, Any]] | None = None
        self._timestamp: float = 0.0

    @property
    def is_valid(self) -> bool:
        if self._data is None:
            return False
        return (time.monotonic() - self._timestamp) < self._ttl

    def get(self) -> list[dict[str, Any]] | None:
        if self.is_valid:
            return self._data
        return None

    def set(self, data: list[dict[str, Any]]) -> None:
        self._data = data
        self._timestamp = time.monotonic()

    def invalidate(self) -> None:
        self._data = None
        self._timestamp = 0.0
