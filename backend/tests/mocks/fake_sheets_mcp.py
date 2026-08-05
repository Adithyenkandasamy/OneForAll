"""Local fake Google Sheets MCP server for offline tests.

Implements the same tool surface as the real Smithery Google Sheets MCP
server (toolbox) so tests exercise the identical client path without
network access or API keys.

Run standalone via stdio:
    uv run python -m tests.mocks.fake_sheets_mcp

It is registered as an MCP server in app/shared/mcp/servers.json under
the name "toolbox_fake"; point MCP_SHEETS_SERVER_NAME at it in tests.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("fake-sheets")

SHEET_DATA: dict[str, list[dict[str, str]]] = {
    "inventory": [
        {"sku": "BOLT-M10", "name": "Hex Bolt M10", "qty": "1200", "reorder": "500", "status": "OK"},
        {"sku": "RAW-STL-01", "name": "Steel Raw 12mm", "qty": "80", "reorder": "200", "status": "LOW"},
        {"sku": "LUBE-5W", "name": "Lubricant 5W-30", "qty": "34", "reorder": "50", "status": "LOW"},
        {"sku": "WELD-ROD", "name": "Welding Rod 2.5mm", "qty": "10", "reorder": "100", "status": "STOCKOUT"},
    ]
}


@mcp.tool()
def read_sheet(sheet: str = "inventory", range: str = "A1:E10") -> list[dict[str, str]]:
    """Read rows from a sheet."""
    return SHEET_DATA.get(sheet, [])


@mcp.tool()
def search_sheet(query: str, sheet: str = "inventory") -> list[dict[str, str]]:
    """Search a sheet for rows whose values contain the query."""
    return [
        row
        for row in SHEET_DATA.get(sheet, [])
        if query.lower() in " ".join(row.values()).lower()
    ]


@mcp.tool()
def get_row(sku: str, sheet: str = "inventory") -> dict[str, str] | None:
    """Get a single row by SKU."""
    for row in SHEET_DATA.get(sheet, []):
        if row.get("sku") == sku:
            return row
    return None


@mcp.tool()
def append_row(values: list[str], sheet: str = "inventory") -> str:
    """Append a row to a sheet. Returns the new row reference."""
    row = {k: v for k, v in zip(SHEET_DATA.get(sheet, [{}])[0], values)}
    SHEET_DATA.setdefault(sheet, []).append(row)
    return f"{sheet}!{len(SHEET_DATA[sheet])}"


@mcp.tool()
def update_cell(sku: str, column: str, value: str, sheet: str = "inventory") -> str:
    """Update a single cell for the row matching sku. Returns confirmation."""
    for row in SHEET_DATA.get(sheet, []):
        if row.get("sku") == sku:
            row[column] = value
            return f"updated {sku}.{column} = {value}"
    return "row not found"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
