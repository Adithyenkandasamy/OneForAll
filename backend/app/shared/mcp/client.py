"""Typed MCP client wrapping a session to one configured server.

Maintains a single persistent connection to the MCP server via a background thread
to avoid the overhead and teardown bugs of spinning up a subprocess on every poll.
"""

from __future__ import annotations

import asyncio
import json
import threading
from typing import Any

from mcp import ClientSession

from app.core.exceptions import McpUnavailableError
from app.core.logging import get_logger
from app.shared.llm.base import ToolDefinition
from app.shared.mcp.transport import connect_server

logger = get_logger(__name__)

# Singleton global state
_sessions: dict[str, ClientSession] = {}
_loops: dict[str, asyncio.AbstractEventLoop] = {}
_threads: dict[str, threading.Thread] = {}
_lock = threading.Lock()


def _describe(exc: BaseException) -> str:
    message = str(exc).strip()
    return message or type(exc).__name__


def _run_background_loop(server_url: str, server: dict[str, Any]):
    """Runs a dedicated event loop in a background thread for a long-lived MCP session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _loops[server_url] = loop

    async def _runner():
        try:
            async for read, write in connect_server(server):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    _sessions[server_url] = session
                    
                    # Keep the session alive indefinitely until the loop stops
                    stop_event = asyncio.Event()
                    await stop_event.wait()
        except Exception as e:
            logger.error("Background MCP loop crashed", extra={"error": str(e)})

    try:
        loop.run_until_complete(_runner())
    finally:
        loop.close()


def _ensure_session(server: dict[str, Any]) -> tuple[ClientSession, asyncio.AbstractEventLoop]:
    server_url = server.get("url") or server.get("command") or "default"
    
    with _lock:
        if server_url in _sessions and server_url in _loops:
            return _sessions[server_url], _loops[server_url]
        
        if server_url not in _threads:
            t = threading.Thread(target=_run_background_loop, args=(server_url, server), daemon=True)
            t.start()
            _threads[server_url] = t
            
    # Wait for the session to initialize
    import time
    for _ in range(50):
        if server_url in _sessions:
            return _sessions[server_url], _loops[server_url]
        time.sleep(0.1)
        
    raise McpUnavailableError("Failed to initialize background MCP session in time")


async def list_tools(server: dict[str, Any]) -> list[ToolDefinition]:
    session, loop = _ensure_session(server)
    
    # Use loop.run_coroutine_threadsafe to interact with the background loop
    future = asyncio.run_coroutine_threadsafe(session.list_tools(), loop)
    result = await asyncio.wrap_future(future)
    
    return [
        ToolDefinition(
            name=tool.name,
            description=tool.description or "",
            input_schema=tool.inputSchema or {"type": "object", "properties": {}},
        )
        for tool in result.tools
    ]


async def call_tool(server: dict[str, Any], name: str, arguments: dict[str, Any]) -> Any:
    session, loop = _ensure_session(server)
    
    future = asyncio.run_coroutine_threadsafe(session.call_tool(name, arguments=arguments), loop)
    result = await asyncio.wrap_future(future)
    
    return _extract_text(result)


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
