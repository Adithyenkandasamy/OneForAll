"""Integration test against the real Smithery Google Sheets MCP server.

Requires SMITHIRY_AI + SMITHIRY_SPACE in the environment/.env. Tests are
skipped when the server is unreachable (e.g. missing/expired credentials).
"""

from __future__ import annotations

import pytest

from app.shared.mcp import client as mcp_client
from app.shared.mcp.manager import get_server

_SERVER_NAME = "toolbox"


@pytest.mark.asyncio
async def test_list_tools_returns_real_sheet_surface():
    server = get_server(_SERVER_NAME)
    try:
        tools = await mcp_client.list_tools(server)
    except Exception as exc:
        pytest.skip(f"Smithery server unreachable: {exc}")
    names = {tool.name for tool in tools}
    assert names, "Smithery server returned no tools"


@pytest.mark.asyncio
async def test_sheets_tools_are_callable():
    server = get_server(_SERVER_NAME)
    try:
        tools = await mcp_client.list_tools(server)
    except Exception as exc:
        pytest.skip(f"Smithery server unreachable: {exc}")
    names = {tool.name for tool in tools}
    assert "search_toolbox" in names and "execute" in names
