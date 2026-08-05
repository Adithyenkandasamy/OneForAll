"""MCP transport adapters: stdio and streamable HTTP.

Each returns an async context manager yielding ``(read, write)`` streams
compatible with ``mcp.ClientSession``.

NOTE: mcp<2's ``streamable_http_client`` has an anyio teardown bug on the
error path (``RuntimeError: Attempted to exit cancel scope in a different
task than it was entered in``). We suppress that spurious error here so a
failed MCP call never crashes the request; the original error is preserved
and re-raised by the client layer.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from typing import Any

import httpx
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_CANCEL_SCOPE_MARKERS = ("cancel scope", "cancel_scope")


def _is_teardown_bug(exc: Exception) -> bool:
    return any(marker in str(exc) for marker in _CANCEL_SCOPE_MARKERS)


async def connect_stdio(server: dict[str, Any]):
    params = StdioServerParameters(
        command=server["command"],
        args=list(server.get("args", [])),
        env={**os.environ, **server.get("env", {})},
    )
    ctx = stdio_client(params)
    async with ctx as (read, write):
        yield read, write


async def connect_http(server: dict[str, Any]):
    headers = server.get("headers") or {}
    timeout = httpx.Timeout(settings.mcp_tool_timeout_seconds, read=60.0)
    http_client = httpx.AsyncClient(headers=headers, timeout=timeout)
    ctx = streamable_http_client(server["url"], http_client=http_client)
    try:
        try:
            async with ctx as (read, write, _get_session_id):
                yield read, write
        except RuntimeError as exc:
            if not _is_teardown_bug(exc):
                raise
            logger.debug("Suppressed MCP cancel-scope teardown error")
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
