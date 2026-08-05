"""Integration test against the real mcp-gsheets MCP server (stdio via npx).

Requires GOOGLE_PROJECT_ID + GOOGLE_APPLICATION_CREDENTIALS (and a reachable
node/npx) in the environment/.env. Tests are skipped when the server is
unreachable (e.g. missing credentials or no network).
"""

from __future__ import annotations

import pytest

from app.shared.mcp import client as mcp_client
from app.shared.mcp.manager import get_server

_SERVER_NAME = "gsheets"


@pytest.mark.asyncio
async def test_list_tools_returns_real_sheet_surface():
    try:
        server = get_server(_SERVER_NAME)
        tools = await mcp_client.list_tools(server)
    except Exception as exc:
        pytest.skip(f"mcp-gsheets server unreachable: {exc}")
    names = {tool.name for tool in tools}
    assert names, "mcp-gsheets server returned no tools"
    assert "sheets_get_values" in names
    assert "sheets_append_values" in names
