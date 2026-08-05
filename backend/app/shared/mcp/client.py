"""Typed MCP client wrapping a session to one configured server.

The rest of the platform interacts with Google Sheets ONLY through this
client. The agent-facing abstraction lives in ``app/shared/agents``.

IMPORTANT: never ``return``/``break`` from inside an ``async for`` over a
transport generator — abandoning the generator corrupts the anyio cancel
scope. The session helper exhausts the transport fully before returning.
"""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from mcp import ClientSession

from app.core.exceptions import McpUnavailableError
from app.core.logging import get_logger
from app.shared.llm.base import ToolDefinition
from app.shared.mcp.transport import connect_server

logger = get_logger(__name__)

T = TypeVar("T")

_SessionFn = Callable[[ClientSession], Awaitable[T]]


async def _with_session(server: dict[str, Any], fn: _SessionFn[T]) -> T:
    result: T | None = None
    try:
        async for read, write in connect_server(server):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await fn(session)
    except McpUnavailableError:
        raise
    except Exception as exc:  # transport / init failures
        logger.warning("MCP session failed", extra={"server": server.get("url"), "error": str(exc)})
        raise McpUnavailableError(f"MCP server unreachable: {exc}") from exc
    if result is None:
        raise McpUnavailableError("MCP connection yielded no session")
    return result


async def list_tools(server: dict[str, Any]) -> list[ToolDefinition]:
    async def _list(session: ClientSession) -> list[ToolDefinition]:
        result = await session.list_tools()
        return [
            ToolDefinition(
                name=tool.name,
                description=tool.description or "",
                input_schema=tool.inputSchema or {"type": "object", "properties": {}},
            )
            for tool in result.tools
        ]

    return await _with_session(server, _list)


async def call_tool(server: dict[str, Any], name: str, arguments: dict[str, Any]) -> Any:
    async def _call(session: ClientSession) -> Any:
        result = await session.call_tool(name, arguments=arguments)
        return _extract_text(result)

    return await _with_session(server, _call)


def _extract_text(result: Any) -> Any:
    items = [
        item
        for item in getattr(result, "content", []) or []
        if getattr(item, "type", None) == "text"
    ]
    if not items:
        return result
    parsed: list[Any] = []
    for item in items:
        try:
            parsed.append(json.loads(item.text))
        except json.JSONDecodeError:
            parsed.append(item.text)
    return parsed[0] if len(parsed) == 1 else parsed
