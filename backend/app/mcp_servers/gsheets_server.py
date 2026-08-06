"""Custom MCP Server for Google Sheets with Read + Write support.

Replaces the generic read-only mcp-gsheets npm package with a full-featured
server that supports both reading and writing to Google Sheets via gspread.
"""

from __future__ import annotations

import json
import os
from typing import Any

import gspread
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


load_dotenv()

CREDENTIALS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
SPREADSHEET_ID = os.environ.get("SHEETS_SPREADSHEET_ID")
SHEET_NAME = os.environ.get("SHEETS_RANGE", "Sheet1!A1:H1000").split("!")[0]

if not CREDENTIALS_PATH or not SPREADSHEET_ID:
    raise RuntimeError(
        "Missing GOOGLE_APPLICATION_CREDENTIALS or SHEETS_SPREADSHEET_ID in environment"
    )

gc = gspread.service_account(filename=CREDENTIALS_PATH)
spreadsheet = gc.open_by_key(SPREADSHEET_ID)
ws = spreadsheet.worksheet(SHEET_NAME)


server = Server("google-sheets")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_sheet_data",
            description="Get all data from the sheet as a list of records (objects).",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_cell",
            description="Get the value of a specific cell by row and column (1-indexed).",
            inputSchema={
                "type": "object",
                "properties": {
                    "row": {"type": "integer", "description": "Row number (1-indexed)"},
                    "col": {"type": "integer", "description": "Column number (1-indexed)"},
                },
                "required": ["row", "col"],
            },
        ),
        Tool(
            name="get_row",
            description="Get all values in a specific row (1-indexed).",
            inputSchema={
                "type": "object",
                "properties": {
                    "row": {"type": "integer", "description": "Row number (1-indexed)"},
                },
                "required": ["row"],
            },
        ),
        Tool(
            name="get_column",
            description="Get all values in a specific column by letter (e.g., 'A', 'B').",
            inputSchema={
                "type": "object",
                "properties": {
                    "col_letter": {"type": "string", "description": "Column letter (e.g., 'A', 'B')"},
                },
                "required": ["col_letter"],
            },
        ),
        Tool(
            name="find_row_by_value",
            description="Find the first row number where a column contains a specific value.",
            inputSchema={
                "type": "object",
                "properties": {
                    "col_letter": {"type": "string", "description": "Column letter to search in"},
                    "value": {"type": "string", "description": "Value to find"},
                },
                "required": ["col_letter", "value"],
            },
        ),
        Tool(
            name="update_cell",
            description="Update a specific cell value by row and column (1-indexed).",
            inputSchema={
                "type": "object",
                "properties": {
                    "row": {"type": "integer", "description": "Row number (1-indexed)"},
                    "col": {"type": "integer", "description": "Column number (1-indexed)"},
                    "value": {"type": "string", "description": "New value to set"},
                },
                "required": ["row", "col", "value"],
            },
        ),
        Tool(
            name="update_row",
            description="Update an entire row with new values (1-indexed).",
            inputSchema={
                "type": "object",
                "properties": {
                    "row": {"type": "integer", "description": "Row number (1-indexed)"},
                    "values": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of values to set in the row",
                    },
                },
                "required": ["row", "values"],
            },
        ),
        Tool(
            name="append_row",
            description="Append a new row at the end of the sheet.",
            inputSchema={
                "type": "object",
                "properties": {
                    "values": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of values for the new row",
                    },
                },
                "required": ["values"],
            },
        ),
        Tool(
            name="batch_update_cells",
            description="Update multiple cells at once using A1 notation ranges.",
            inputSchema={
                "type": "object",
                "properties": {
                    "updates": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "range": {"type": "string", "description": "A1 notation range (e.g., 'A1:B2')"},
                                "values": {
                                    "type": "array",
                                    "items": {"type": "array", "items": {"type": "string"}},
                                    "description": "2D array of values",
                                },
                            },
                            "required": ["range", "values"],
                        },
                        "description": "List of range updates",
                    },
                },
                "required": ["updates"],
            },
        ),
        Tool(
            name="clear_range",
            description="Clear values in a specific range (A1 notation).",
            inputSchema={
                "type": "object",
                "properties": {
                    "range": {"type": "string", "description": "A1 notation range (e.g., 'A1:C10')"},
                },
                "required": ["range"],
            },
        ),
    ]


def _col_letter_to_index(letter: str) -> int:
    """Convert column letter (A, B, ..., Z, AA, etc.) to 1-indexed number."""
    result = 0
    for char in letter.upper():
        result = result * 26 + (ord(char) - ord("A") + 1)
    return result


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        if name == "get_sheet_data":
            records = ws.get_all_records()
            return [TextContent(type="text", text=json.dumps(records, default=str))]

        elif name == "get_cell":
            row = int(arguments["row"])
            col = int(arguments["col"])
            value = ws.cell(row, col).value
            return [TextContent(type="text", text=json.dumps({"row": row, "col": col, "value": value}))]

        elif name == "get_row":
            row = int(arguments["row"])
            values = ws.row_values(row)
            return [TextContent(type="text", text=json.dumps({"row": row, "values": values}))]

        elif name == "get_column":
            col_letter = arguments["col_letter"]
            col_index = _col_letter_to_index(col_letter)
            values = ws.col_values(col_index)
            return [TextContent(type="text", text=json.dumps({"column": col_letter, "values": values}))]

        elif name == "find_row_by_value":
            col_letter = arguments["col_letter"]
            search_value = arguments["value"]
            col_index = _col_letter_to_index(col_letter)
            values = ws.col_values(col_index)
            for i, val in enumerate(values, start=1):
                if str(val).lower() == str(search_value).lower():
                    return [TextContent(type="text", text=json.dumps({"row": i, "value": val}))]
            return [TextContent(type="text", text=json.dumps({"error": f"Value '{search_value}' not found in column {col_letter}"}))]

        elif name == "update_cell":
            row = int(arguments["row"])
            col = int(arguments["col"])
            value = str(arguments["value"])
            ws.update_cell(row, col, value)
            return [TextContent(type="text", text=json.dumps({"success": True, "message": f"Updated cell ({row}, {col}) to '{value}'"}))]

        elif name == "update_row":
            row = int(arguments["row"])
            values = [str(v) for v in arguments["values"]]
            ws.update_row(row, values)
            return [TextContent(type="text", text=json.dumps({"success": True, "message": f"Updated row {row} with {len(values)} values"}))]

        elif name == "append_row":
            values = [str(v) for v in arguments["values"]]
            ws.append_row(values)
            return [TextContent(type="text", text=json.dumps({"success": True, "message": f"Appended new row with {len(values)} values"}))]

        elif name == "batch_update_cells":
            updates = arguments["updates"]
            for update in updates:
                ws.update(update["range"], update["values"])
            return [TextContent(type="text", text=json.dumps({"success": True, "message": f"Applied {len(updates)} range updates"}))]

        elif name == "clear_range":
            range_str = arguments["range"]
            ws.clear(range_str)
            return [TextContent(type="text", text=json.dumps({"success": True, "message": f"Cleared range {range_str}"}))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": f"Tool '{name}' failed: {str(e)}"}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
