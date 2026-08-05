"""Unit tests for the per-service MCP server config loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.shared.mcp import manager


def _write(tmp_path: Path, name: str, data: object) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_load_servers_merges_per_service_files(tmp_path, monkeypatch):
    monkeypatch.setattr(manager, "SERVERS_DIR", tmp_path)
    _write(
        tmp_path,
        "gsheets.json",
        {
            "mcpServers": {
                "gsheets": {
                    "type": "stdio",
                    "command": "npx",
                    "args": ["-y", "mcp-gsheets@latest"],
                    "env": {"GOOGLE_PROJECT_ID": "${GOOGLE_PROJECT_ID}"},
                }
            }
        },
    )
    _write(tmp_path, "other.json", {"other": {"type": "stdio", "command": "foo"}})
    monkeypatch.setenv("GOOGLE_PROJECT_ID", "my-project")

    servers = manager.load_servers()

    assert set(servers) == {"gsheets", "other"}
    assert servers["gsheets"]["env"]["GOOGLE_PROJECT_ID"] == "my-project"
    assert servers["other"]["command"] == "foo"


def test_load_servers_accepts_flat_file_without_mcpservers_key(tmp_path):
    path = _write(tmp_path, "flat.json", {"flat": {"type": "stdio", "command": "cat"}})
    servers = manager.load_servers(path)
    assert servers["flat"]["command"] == "cat"


def test_missing_env_var_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(manager, "SERVERS_DIR", tmp_path)
    var = "MISSING_ENV_VAR_FOR_TEST"
    cfg = {"gsheets": {"env": {var: "${" + var + "}"}}}
    _write(tmp_path, "gsheets.json", cfg)
    monkeypatch.delenv(var, raising=False)
    with pytest.raises(manager.McpConfigError, match=var):
        manager.load_servers()


def test_duplicate_server_names_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(manager, "SERVERS_DIR", tmp_path)
    _write(tmp_path, "a.json", {"gsheets": {"command": "npx"}})
    _write(tmp_path, "b.json", {"gsheets": {"command": "npx"}})
    with pytest.raises(manager.McpConfigError, match="Duplicate MCP server 'gsheets'"):
        manager.load_servers()


def test_get_server_unknown_name(tmp_path, monkeypatch):
    monkeypatch.setattr(manager, "SERVERS_DIR", tmp_path)
    _write(tmp_path, "gsheets.json", {"gsheets": {"command": "npx"}})
    with pytest.raises(manager.McpConfigError, match="Available servers: gsheets"):
        manager.get_server("missing")
