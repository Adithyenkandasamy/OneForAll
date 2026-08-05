"""Inventory agent ports (interfaces the agent depends on).

Defined here so the agent depends only on abstractions. The composition
root supplies the concrete implementations, which keeps the agent package
free of app-layer imports and testable with fakes.
"""

from __future__ import annotations

from typing import Any, Protocol

from app.shared.llm.base import ToolDefinition


class McpGateway(Protocol):
    """Bound to the Google Sheets MCP server (only sheet interaction)."""

    async def list_tools(self) -> list[ToolDefinition]: ...

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any: ...


class HistorySink(Protocol):
    """Persists AI analysis records to platform-owned storage."""

    async def save(self, record: dict[str, Any]) -> None: ...


class RiskExtractor(Protocol):
    """Extracts machine-readable risk flags from an agent answer."""

    async def extract(self, content: str) -> list[str]: ...
