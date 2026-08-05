"""MCP Gateway for the custom inventory-analytics server.

Thin wrapper that calls the local inventory MCP server via stdio.
"""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.exceptions import McpUnavailableError
from app.core.logging import get_logger
from app.shared.llm.base import ToolDefinition
from app.shared.mcp import client as mcp_client
from app.shared.mcp.manager import get_server

logger = get_logger(__name__)

ALL_TOOLS = (
    "get_material",
    "search_materials",
    "get_supplier_stats",
    "get_low_stock",
    "query_inventory",
    "get_columns",
    "update_cell",
)

READ_TOOLS = tuple(t for t in ALL_TOOLS if t != "update_cell")


class InventoryMcpGateway:
    """Gateway to the custom inventory-analytics MCP server."""

    def __init__(self, server: dict[str, Any] | None = None) -> None:
        self._server = server

    def _resolve_server(self) -> dict[str, Any]:
        if self._server is not None:
            return self._server
        try:
            return get_server("inventory-analytics")
        except ValueError as exc:
            raise McpUnavailableError(str(exc)) from exc

    async def list_tools(self) -> list[ToolDefinition]:
        try:
            return await mcp_client.list_tools(self._resolve_server())
        except McpUnavailableError:
            raise
        except Exception as exc:
            logger.warning("Failed to list inventory MCP tools", extra={"error": str(exc)})
            raise McpUnavailableError(f"Inventory MCP unavailable: {exc}") from exc

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        try:
            return await mcp_client.call_tool(self._resolve_server(), name, arguments or {})
        except McpUnavailableError:
            raise
        except Exception as exc:
            logger.warning("Inventory MCP tool call failed", extra={"tool": name, "error": str(exc)})
            raise McpUnavailableError(f"Inventory MCP tool {name!r} failed: {exc}") from exc

SheetsMcpGateway = InventoryMcpGateway