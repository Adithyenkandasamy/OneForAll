"""Google Sheets MCP tool surface for the inventory agent.

The configured MCP server is ``mcp-gsheets`` (freema), a stdio server started
via ``npx`` that exposes ``sheets_*`` tools. Those tools take a
``spreadsheetId`` and A1 ranges — the agent never sees these internals.

This gateway exposes a small semantic surface (read/search/get/append/update)
and translates each call to the real ``sheets_*`` tool, injecting the
configured spreadsheet id/range. Missing credentials or an unreachable server
surface as ``McpUnavailableError`` with an actionable message.
"""

from __future__ import annotations

import json
from typing import Any

from app.core.config import settings
from app.core.exceptions import McpUnavailableError
from app.core.logging import get_logger
from app.shared.llm.base import ToolDefinition
from app.shared.mcp import client as mcp_client
from app.shared.mcp.manager import get_server

logger = get_logger(__name__)

# Tool semantics used by the inventory agent; the gateway maps each of these
# onto the live mcp-gsheets tools at call time.
READ_TOOLS = ("read_sheet", "search_sheet", "get_row")
WRITE_TOOLS = ("append_row", "update_cell")

ALL_TOOLS = READ_TOOLS + WRITE_TOOLS

_SEMANTIC_TOOLS = [
    ToolDefinition(
        name="read_sheet",
        description=(
            "Read the full inventory sheet. Returns one object per row keyed by "
            "the header row (sku, name, qty, reorder, unit, status)."
        ),
        input_schema={"type": "object", "properties": {}},
    ),
    ToolDefinition(
        name="search_sheet",
        description=(
            "Search inventory rows for a substring across all columns. Returns "
            "matching rows keyed by the header row."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Text to search for in any column"}
            },
            "required": ["query"],
        },
    ),
    ToolDefinition(
        name="get_row",
        description="Fetch a single inventory row by SKU. Returns the row keyed by the header row.",
        input_schema={
            "type": "object",
            "properties": {"sku": {"type": "string"}},
            "required": ["sku"],
        },
    ),
    ToolDefinition(
        name="append_row",
        description=(
            "Append a new inventory row. Pass values as an object mapping column "
            "names to values, e.g. {'sku': 'BOLT-M10', 'qty': 100}."
        ),
        input_schema={
            "type": "object",
            "properties": {"values": {"type": "object", "description": "Column -> value map"}},
            "required": ["values"],
        },
    ),
    ToolDefinition(
        name="update_cell",
        description=(
            "Update a single cell of an existing inventory row, identified by SKU. "
            "Column is a header name such as qty, reorder, or status."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "sku": {"type": "string"},
                "column": {"type": "string"},
                "value": {"type": "string"},
            },
            "required": ["sku", "column", "value"],
        },
    ),
]

_DEFAULT_HEADER = ["sku", "name", "qty", "reorder", "unit", "status"]

_HEADER_ALIASES = {
    "reorder_point": "reorder",
    "reorder": "reorder",
    "min": "reorder",
    "minimum": "reorder",
    "safety_stock": "reorder",
    "qty": "qty",
    "quantity": "qty",
    "stock": "qty",
    "on_hand": "qty",
    "sku": "sku",
    "name": "name",
    "item": "name",
    "product": "name",
    "part": "name",
    "unit": "unit",
    "uom": "unit",
    "status": "status",
}


def _canonical_key(header_cell: Any) -> str:
    key = str(header_cell).strip().lower().replace(" ", "_")
    return _HEADER_ALIASES.get(key, key)


def _normalise_values(result: Any) -> list[list[Any]]:
    """Coerce an mcp-gsheets read result into a list of row lists."""
    values: Any = None
    if isinstance(result, dict):
        values = result.get("values") or result.get("rows")
    elif isinstance(result, str):
        try:
            parsed = json.loads(result)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            values = parsed.get("values") or parsed.get("rows")
        elif isinstance(parsed, list):
            values = parsed
    elif isinstance(result, list):
        values = result
    if not isinstance(values, list):
        return []
    return [row if isinstance(row, list) else [row] for row in values]


def _rows_to_dicts(values: list[list[Any]]) -> list[dict[str, Any]]:
    if not values:
        return []
    header = [_canonical_key(cell) for cell in values[0]]
    rows: list[dict[str, Any]] = []
    for row in values[1:]:
        padded = list(row) + [""] * (len(header) - len(row))
        rows.append({header[i]: padded[i] for i in range(len(header))})
    return rows


def _column_letter(index: int) -> str:
    result = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        result = chr(65 + rem) + result
    return result


def _range_parts(range_: str) -> tuple[str, int]:
    tab = range_
    start_row = 1
    if "!" in range_:
        tab, a1 = range_.split("!", 1)
        digits = "".join(ch for ch in a1.split(":", 1)[0] if ch.isdigit())
        if digits:
            start_row = int(digits)
    return tab, start_row


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

    def _spreadsheet_id(self, arguments: dict[str, Any]) -> str:
        return str(arguments.get("spreadsheetId") or settings.sheets_spreadsheet_id or "")

    def _range(self, arguments: dict[str, Any]) -> str:
        return str(arguments.get("range") or settings.sheets_range or "")

    async def _mcp_call(self, name: str, arguments: dict[str, Any]) -> Any:
        try:
            return await mcp_client.call_tool(self._resolve_server(), name, arguments)
        except McpUnavailableError as exc:
            raise McpUnavailableError(f"Google Sheets is unreachable: {exc.message}") from exc

    async def _read_values(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        result = await self._mcp_call(
            "sheets_get_values",
            {
                "spreadsheetId": self._spreadsheet_id(arguments),
                "range": self._range(arguments),
                "valueRenderOption": arguments.get("valueRenderOption", "FORMATTED_VALUE"),
            },
        )
        return _rows_to_dicts(_normalise_values(result))

    async def _handle_read(self, arguments: dict[str, Any]) -> Any:
        return await self._read_values(arguments)

    async def _handle_search(self, arguments: dict[str, Any]) -> Any:
        query = str(arguments.get("query", "")).lower()
        rows = await self._read_values(arguments)
        if not query:
            return rows
        return [
            row
            for row in rows
            if query in " ".join(str(value) for value in row.values()).lower()
        ]

    async def _handle_get_row(self, arguments: dict[str, Any]) -> Any:
        sku = str(arguments.get("sku", "")).lower()
        rows = await self._read_values(arguments)
        return next((row for row in rows if str(row.get("sku", "")).lower() == sku), [])

    async def _handle_append(self, arguments: dict[str, Any]) -> Any:
        values = arguments.get("values")
        if not isinstance(values, dict) or not values:
            raise McpUnavailableError(
                "append_row requires a 'values' object mapping column names to values"
            )
        existing = await self._read_values(arguments)
        header = list(existing[0].keys()) if existing else _DEFAULT_HEADER
        row_values = [values.get(key, "") for key in header]
        return await self._mcp_call(
            "sheets_append_values",
            {
                "spreadsheetId": self._spreadsheet_id(arguments),
                "range": self._range(arguments),
                "values": [row_values],
                "valueInputOption": arguments.get("valueInputOption", "USER_ENTERED"),
                "insertDataOption": "INSERT_ROWS",
            },
        )

    async def _handle_update(self, arguments: dict[str, Any]) -> Any:
        sku = str(arguments.get("sku", "")).strip()
        column = _canonical_key(arguments.get("column", ""))
        value = str(arguments.get("value", ""))
        if not sku or not column:
            raise McpUnavailableError("update_cell requires 'sku', 'column', and 'value'")
        rows = await self._read_values(arguments)
        header = list(rows[0].keys()) if rows else []
        if column not in header:
            raise McpUnavailableError(f"Column {column!r} not found in the inventory sheet")
        col_index = header.index(column)
        match = next(
            (row for row in rows if str(row.get("sku", "")).lower() == sku.lower()), None
        )
        if match is None:
            raise McpUnavailableError(f"SKU {sku!r} not found in the inventory sheet")
        row_index = rows.index(match)
        tab, start_row = _range_parts(self._range(arguments))
        cell_range = f"{tab}!{_column_letter(col_index)}{start_row + row_index + 1}"
        return await self._mcp_call(
            "sheets_update_values",
            {
                "spreadsheetId": self._spreadsheet_id(arguments),
                "range": cell_range,
                "values": [[value]],
                "valueInputOption": arguments.get("valueInputOption", "USER_ENTERED"),
            },
        )

    async def list_tools(self) -> list[ToolDefinition]:
        return list(_SEMANTIC_TOOLS)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        arguments = arguments or {}
        handlers = {
            "read_sheet": self._handle_read,
            "search_sheet": self._handle_search,
            "get_row": self._handle_get_row,
            "append_row": self._handle_append,
            "update_cell": self._handle_update,
        }
        handler = handlers.get(name)
        if handler is None:
            raise McpUnavailableError(f"Unknown inventory tool {name!r}")
        return await handler(arguments)
