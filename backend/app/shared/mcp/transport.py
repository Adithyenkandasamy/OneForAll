"""MCP transport adapters: stdio and streamable HTTP.

Each returns an async context manager yielding ``(read, write)`` streams
compatible with ``mcp.ClientSession``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import httpx
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client


async def connect_stdio(server: dict[str, Any]):
    params = StdioServerParameters(command=server["command"], args=list(server.get("args", [])))
    ctx = stdio_client(params)
    async with ctx as (read, write):
        yield read, write


async def connect_http(server: dict[str, Any]):
    headers = server.get("headers") or {}
    http_client = httpx.AsyncClient(headers=headers)
    ctx = streamable_http_client(server["url"], http_client=http_client)
    try:
        async with ctx as (read, write, _get_session_id):
            yield read, write
    finally:
        await http_client.aclose()


async def connect_server(server: dict[str, Any]) -> AsyncIterator[tuple[Any, Any]]:
    transport = server.get("type", "stdio")
    if transport == "http":
        async for streams in connect_http(server):
            yield streams
    else:
        async for streams in connect_stdio(server):
            yield streams
