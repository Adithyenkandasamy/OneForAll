"""Unit tests for the MCP client's session wrapper error handling.

The real mcp stdio/http transports can raise noise (cancel-scope teardown
bugs, exception groups from the stdio TaskGroup) on the error path. These
tests pin that such noise surfaces as a clean ``McpUnavailableError`` and
never as a raw ``RuntimeError``.
"""

from __future__ import annotations

import pytest
from exceptiongroup import BaseExceptionGroup

from app.core.exceptions import McpUnavailableError
from app.shared.mcp import client as mcp_client

SERVER = {"type": "stdio", "command": "npx"}


@pytest.mark.asyncio
async def test_cancel_scope_noise_becomes_unavailable(monkeypatch):
    async def noisy_transport(server: dict) -> object:
        raise RuntimeError(
            "Attempted to exit cancel scope in a different task than it was entered in"
        )
        yield  # pragma: no cover

    monkeypatch.setattr(mcp_client, "connect_server", noisy_transport)
    with pytest.raises(McpUnavailableError, match="MCP server unreachable"):
        await mcp_client.list_tools(SERVER)


@pytest.mark.asyncio
async def test_exception_group_becomes_unavailable(monkeypatch):
    async def group_transport(server: dict) -> object:
        raise BaseExceptionGroup(
            "unhandled errors in a TaskGroup",
            [RuntimeError("cancel scope teardown")],
        )
        yield  # pragma: no cover

    monkeypatch.setattr(mcp_client, "connect_server", group_transport)
    with pytest.raises(McpUnavailableError, match="cancel scope teardown"):
        await mcp_client.list_tools(SERVER)
