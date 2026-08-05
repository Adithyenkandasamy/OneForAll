"""Google Sheets MCP tool surface for the inventory agent.

Defines the tool allow-list and the McpGateway adapter bound to the
configured sheets MCP server. The agent NEVER calls Google Sheets APIs
directly — every interaction flows through this gateway.
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

READ_TOOLS = ("read_sheet", "search_sheet", "get_row")
WRITE_TOOLS = ("append_row", "update_cell")

ALL_TOOLS = READ_TOOLS + WRITE_TOOLS


class SheetsMcpGateway:
    """McpGateway implementation bound to the sheets MCP server config."""

    def __init__(self, server: dict[str, Any] | None = None) -> None:
        self._server = server

    def _resolve_server(self) -> dict[str, Any]:
        if self._server is not None:
            return self._server
        try:
            return get_server(settings.mcp_sheets_server_name)
        except ValueError as exc:
            raise McpUnavailableError(str(exc)) from exc

    async def list_tools(self) -> list[ToolDefinition]:
        return await mcp_client.list_tools(self._resolve_server())

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        return await mcp_client.call_tool(self._resolve_server(), name, arguments)
