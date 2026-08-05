"""Unit tests for the SheetsMcpGateway translation layer.

The gateway exposes a semantic tool surface and translates each call to the
real mcp-gsheets ``sheets_*`` tools. These tests stub the low-level MCP client
so no live server or credentials are required.
"""

from __future__ import annotations

import pytest

from app.agents.inventory import mcp_tools
from app.agents.inventory.mcp_tools import ALL_TOOLS, SheetsMcpGateway
from app.core.exceptions import McpUnavailableError

SERVER = {"type": "stdio", "command": "npx", "args": ["-y", "mcp-gsheets@latest"], "env": {}}

SHEET_ROWS = [
    ["SKU", "Quantity", "Reorder Point", "Unit"],
    ["BOLT-M10", "1200", "500", "pcs"],
    ["LUBE-5W", "34", "50", "L"],
]

ARGS = {"spreadsheetId": "spr-123", "range": "Inventory!A1:H1000"}


class FakeMcpClient:
    def __init__(self, results: dict | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.results = results or {}

    async def call_tool(self, server: dict, name: str, arguments: dict) -> object:
        self.calls.append((name, arguments))
        if name in self.results:
            return self.results[name]
        return {"values": []}


@pytest.fixture
def fake_mcp(monkeypatch) -> FakeMcpClient:
    fake = FakeMcpClient({"sheets_get_values": {"values": SHEET_ROWS}})
    monkeypatch.setattr(mcp_tools.mcp_client, "call_tool", fake.call_tool)
    return fake


@pytest.mark.asyncio
async def test_list_tools_exposes_semantic_surface():
    gateway = SheetsMcpGateway(SERVER)
    tools = await gateway.list_tools()
    assert [tool.name for tool in tools] == list(ALL_TOOLS)


@pytest.mark.asyncio
async def test_read_sheet_returns_rows_keyed_by_canonical_header(fake_mcp):
    gateway = SheetsMcpGateway(SERVER)
    rows = await gateway.call_tool("read_sheet", ARGS)
    assert rows == [
        {"sku": "BOLT-M10", "qty": "1200", "reorder": "500", "unit": "pcs"},
        {"sku": "LUBE-5W", "qty": "34", "reorder": "50", "unit": "L"},
    ]
    assert fake_mcp.calls[0][0] == "sheets_get_values"
    assert fake_mcp.calls[0][1]["valueRenderOption"] == "FORMATTED_VALUE"


@pytest.mark.asyncio
async def test_search_filters_rows_client_side(fake_mcp):
    gateway = SheetsMcpGateway(SERVER)
    rows = await gateway.call_tool("search_sheet", {"query": "lube"})
    assert [row["sku"] for row in rows] == ["LUBE-5W"]


@pytest.mark.asyncio
async def test_get_row_finds_sku(fake_mcp):
    gateway = SheetsMcpGateway(SERVER)
    row = await gateway.call_tool("get_row", {"sku": "BOLT-M10"})
    assert row["qty"] == "1200"


@pytest.mark.asyncio
async def test_update_cell_computes_correct_cell_range(fake_mcp):
    gateway = SheetsMcpGateway(SERVER)
    await gateway.call_tool(
        "update_cell", {"sku": "LUBE-5W", "column": "qty", "value": "20", **ARGS}
    )
    name, arguments = fake_mcp.calls[1]
    assert name == "sheets_update_values"
    assert arguments["range"] == "Inventory!B3"
    assert arguments["values"] == [["20"]]


@pytest.mark.asyncio
async def test_append_row_aligns_values_to_header(fake_mcp):
    gateway = SheetsMcpGateway(SERVER)
    await gateway.call_tool(
        "append_row", {"values": {"sku": "NUT-M6", "qty": 10}, **ARGS}
    )
    name, arguments = fake_mcp.calls[1]
    assert name == "sheets_append_values"
    assert arguments["values"] == [["NUT-M6", 10, "", ""]]
    assert arguments["insertDataOption"] == "INSERT_ROWS"


@pytest.mark.asyncio
async def test_unknown_tool_raises(fake_mcp):
    gateway = SheetsMcpGateway(SERVER)
    with pytest.raises(McpUnavailableError, match="Unknown inventory tool"):
        await gateway.call_tool("drop_table", {})
