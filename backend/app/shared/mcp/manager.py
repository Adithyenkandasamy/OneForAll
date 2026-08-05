"""MCP server registry: loads app/shared/mcp/servers.json and resolves
environment variables referenced as ${VAR} inside the config.

The API key is NEVER hardcoded — servers.json holds ${SMITHIRY_AI} and
this module substitutes it from the environment (.env is loaded first).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

SERVERS_FILE = Path(__file__).parent / "servers.json"
_ENV_PATTERN = re.compile(r"\${([A-Za-z_][A-Za-z0-9_]*)}")


class McpConfigError(ValueError):
    pass


def _substitute_env(value: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        name = match.group(1)
        resolved = os.environ.get(name)
        if resolved is None or resolved == "":
            raise McpConfigError(
                f"Missing environment variable {name!r} referenced in {SERVERS_FILE.name}"
            )
        return resolved

    return _ENV_PATTERN.sub(_replace, value)


def _resolve(node: Any) -> Any:
    if isinstance(node, dict):
        return {k: _resolve(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_resolve(item) for item in node]
    if isinstance(node, str):
        return _substitute_env(node) if _ENV_PATTERN.search(node) else node
    return node


def load_servers(servers_file: Path = SERVERS_FILE) -> dict[str, dict[str, Any]]:
    """Load all MCP servers from servers.json with env vars substituted."""
    load_dotenv()
    raw = json.loads(servers_file.read_text(encoding="utf-8"))
    servers = raw.get("mcpServers")
    if not isinstance(servers, dict):
        raise McpConfigError(f"{servers_file.name} must contain an 'mcpServers' object")
    return _resolve(servers)


def get_server(name: str, servers_file: Path = SERVERS_FILE) -> dict[str, Any]:
    servers = load_servers(servers_file)
    try:
        return servers[name]
    except KeyError:
        raise McpConfigError(
            f"MCP server {name!r} not found in {servers_file.name}. "
            f"Available: {', '.join(servers)}"
        ) from None
