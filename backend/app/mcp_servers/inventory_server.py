"""Custom MCP Server for Inventory Analytics.

Exposes real analytical tools over Google Sheets data using pandas.
Replaces the generic mcp-gsheets with column-aware, aggregatable queries.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import gspread
import pandas as pd
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
ws = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

df: pd.DataFrame | None = None


def _load_data() -> pd.DataFrame:
    global df
    if df is None:
        records = ws.get_all_records()
        df = pd.DataFrame(records)
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )
    return df


server = Server("inventory-analytics")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_material",
            description="Get a single material row by material_id (exact match).",
            inputSchema={
                "type": "object",
                "properties": {
                    "material_id": {"type": "string", "description": "Material ID to look up (e.g., MAT007)"}
                },
                "required": ["material_id"],
            },
        ),
        Tool(
            name="search_materials",
            description="Search materials by substring across all columns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text to search for"}
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_supplier_stats",
            description="Get frequency count of materials per supplier.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_low_stock",
            description="Get materials where qty <= reorder point.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="query_inventory",
            description="Flexible query with filters. Supports exact, range, and contains operators.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "column": {"type": "string"},
                                "op": {
                                    "type": "string",
                                    "enum": ["==", "!=", ">", ">=", "<", "<=", "contains", "in"],
                                },
                                "value": {"type": ["string", "number", "array"]},
                            },
                            "required": ["column", "op", "value"],
                        },
                    },
                    "limit": {"type": "integer", "default": 100},
                },
            },
        ),
        Tool(
            name="get_columns",
            description="List all column names in the inventory sheet.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="update_cell",
            description="Update a specific cell value by SKU (Exact match) and column name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sku": {"type": "string", "description": "The SKU or material_id of the row to update"},
                    "column": {"type": "string", "description": "The internal column name to update"},
                    "value": {"type": "string", "description": "The new value"}
                },
                "required": ["sku", "column", "value"],
            },
        ),
    ]


def _apply_filters(data: pd.DataFrame, filters: list[dict]) -> pd.DataFrame:
    result = data.copy()
    for f in filters:
        col = f["column"]
        op = f["op"]
        val = f["value"]
        if col not in result.columns:
            continue
        series = result[col].astype(str)
        if op == "==":
            result = result[series == str(val)]
        elif op == "!=":
            result = result[series != str(val)]
        elif op == "contains":
            result = result[series.str.contains(str(val), case=False, na=False)]
        elif op == "in":
            if isinstance(val, list):
                result = result[series.isin([str(v) for v in val])]
        elif op in (">", ">=", "<", "<="):
            try:
                num_series = pd.to_numeric(result[col], errors="coerce")
                num_val = float(val)
                if op == ">":
                    result = result[num_series > num_val]
                elif op == ">=":
                    result = result[num_series >= num_val]
                elif op == "<":
                    result = result[num_series < num_val]
                elif op == "<=":
                    result = result[num_series <= num_val]
            except (ValueError, TypeError):
                pass
    return result


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    global df
    data = _load_data()

    if name == "get_material":
        material_id = str(arguments["material_id"])
        matches = data[data["material_id"].astype(str) == material_id]
        if matches.empty:
            return [TextContent(type="text", text=json.dumps({"error": f"Material {material_id} not found"}))]
        return [TextContent(type="text", text=matches.to_json(orient="records"))]

    elif name == "search_materials":
        query = str(arguments["query"]).lower()
        mask = data.astype(str).apply(lambda row: row.str.contains(query, case=False).any(), axis=1)
        matches = data[mask]
        return [TextContent(type="text", text=matches.to_json(orient="records"))]

    elif name == "get_supplier_stats":
        if "supplier" not in data.columns:
            return [TextContent(type="text", text=json.dumps({"error": "No supplier column found"}))]
        counts = data["supplier"].value_counts().to_dict()
        return [TextContent(type="text", text=json.dumps(counts, indent=2))]

    elif name == "get_low_stock":
        qty_col = next((c for c in data.columns if c.lower() in ("qty", "quantity", "current_stock")), None)
        reorder_col = next((c for c in data.columns if c.lower() in ("reorder", "min", "minimum_stock", "threshold")), None)
        if not qty_col or not reorder_col:
            return [TextContent(type="text", text=json.dumps({"error": f"Missing quantity or threshold column. Available: {list(data.columns)}"}))]
        data["qty_num"] = pd.to_numeric(data[qty_col], errors="coerce")
        data["reorder_num"] = pd.to_numeric(data[reorder_col], errors="coerce")
        low = data[data["qty_num"] <= data["reorder_num"]]
        return [TextContent(type="text", text=low.drop(columns=["qty_num", "reorder_num"]).to_json(orient="records"))]

    elif name == "query_inventory":
        filters = arguments.get("filters", [])
        limit = arguments.get("limit", 100)
        result = _apply_filters(data, filters).head(limit)
        return [TextContent(type="text", text=result.to_json(orient="records"))]

    elif name == "get_columns":
        return [TextContent(type="text", text=json.dumps(list(data.columns)))]

    elif name == "update_cell":
        sku = str(arguments["sku"])
        col_name = str(arguments["column"])
        value = str(arguments["value"])

        if "material_id" not in data.columns and "sku" not in data.columns:
            return [TextContent(type="text", text=json.dumps({"error": "No material_id or sku column found"}))]
        
        key_col = "sku" if "sku" in data.columns else "material_id"
        if col_name not in data.columns:
            return [TextContent(type="text", text=json.dumps({"error": f"Column '{col_name}' not found"}))]

        matches = data[data[key_col].astype(str) == sku]
        if matches.empty:
            return [TextContent(type="text", text=json.dumps({"error": f"SKU '{sku}' not found"}))]

        row_index = matches.index[0]
        col_index = data.columns.get_loc(col_name)

        sheet_row = int(row_index) + 2
        sheet_col = int(col_index) + 1

        try:
            ws.update_cell(sheet_row, sheet_col, value)
            df = None  # Invalidate cache so next read fetches new data
            return [TextContent(type="text", text=json.dumps(
                {"success": True, "message": f"Updated {sku} {col_name} to {value}"}
            ))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": f"Failed to update sheet: {str(e)}"}))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())