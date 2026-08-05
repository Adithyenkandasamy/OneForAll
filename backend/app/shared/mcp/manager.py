"""MCP server registry: loads one JSON file per server from the ``servers``
directory and resolves environment variables referenced as ``${VAR}`` inside
each config.

Credentials are NEVER hardcoded — configs hold ``${VAR}`` placeholders and
this module substitutes them from the environment (.env is loaded first).
Each service owns its file, e.g. ``servers/gsheets.json`` for the inventory
agent's Google Sheets MCP server.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

SERVERS_DIR = Path(__file__).parent / "servers"
_ENV_PATTERN = re.compile(r"\${([A-Za-z_][A-Za-z0-9_]*)}")


class McpConfigError(ValueError):
    pass


def _substitute_env(value: str, source: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        name = match.group(1)
        resolved = os.environ.get(name)
        if resolved is None or resolved == "":
            raise McpConfigError(
                f"Missing environment variable {name!r} referenced in {source}"
            )
        return resolved

    return _ENV_PATTERN.sub(_replace, value)


def _resolve(node: Any, source: str) -> Any:
    if isinstance(node, dict):
        return {k: _resolve(v, source) for k, v in node.items()}
    if isinstance(node, list):
        return [_resolve(item, source) for item in node]
    if isinstance(node, str):
        return _substitute_env(node, source) if _ENV_PATTERN.search(node) else node
    return node


def _entries_of(path: Path) -> dict[str, dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    entries = raw.get("mcpServers", raw) if isinstance(raw, dict) else raw
    if not isinstance(entries, dict):
        raise McpConfigError(f"{path.name} must map server names to config objects")
    return {name: _resolve(cfg, path.name) for name, cfg in entries.items()}


def load_servers(servers_file: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load MCP servers from the per-service config directory (or one file).

    Each ``servers/*.json`` file may hold an ``mcpServers`` object or a flat
    map of server names to configs. Duplicate names across files are rejected.
    """
    load_dotenv()
    paths = [servers_file] if servers_file is not None else sorted(SERVERS_DIR.glob("*.json"))
    servers: dict[str, dict[str, Any]] = {}
    for path in paths:
        for name, cfg in _entries_of(path).items():
            if name in servers:
                raise McpConfigError(f"Duplicate MCP server {name!r} in {path.name}")
            servers[name] = cfg
    return servers


def get_server(name: str, servers_file: Path | None = None) -> dict[str, Any]:
    servers = load_servers(servers_file)
    try:
        return servers[name]
    except KeyError:
        available = ", ".join(servers) or "(none)"
        raise McpConfigError(
            f"MCP server {name!r} not found. Available servers: {available}"
        ) from None
