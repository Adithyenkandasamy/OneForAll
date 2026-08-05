"""Unit tests for the inventory agent: policy, tool allow-list, orchestration."""

from __future__ import annotations

import pytest

from app.agents.inventory.agent import InventoryAgent, _extract_risk_flags
from app.agents.inventory.mcp_tools import ALL_TOOLS, READ_TOOLS
from app.shared.agents.base_agent import AgentContext
from app.shared.llm.base import ToolDefinition
from tests.mocks.fake_llm import FakeLLM, text_response, tool_call_response

INVENTORY_DATA = [
    {"sku": "BOLT-M10", "name": "Hex Bolt M10", "qty": "1200", "reorder": "500", "status": "OK"},
    {"sku": "LUBE-5W", "name": "Lubricant", "qty": "34", "reorder": "50", "status": "LOW"},
]


class FakeGateway:
    def __init__(self, tools: list[ToolDefinition], rows: list[dict]) -> None:
        self._tools = tools
        self._rows = rows
        self.calls: list[tuple[str, dict]] = []

    async def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools)

    async def call_tool(self, name: str, arguments: dict) -> object:
        self.calls.append((name, arguments))
        if name == "search_sheet":
            return [
                row
                for row in self._rows
                if arguments.get("query", "").lower() in " ".join(row.values()).lower()
            ]
        return self._rows


class RecordingSink:
    def __init__(self) -> None:
        self.saved: list[dict] = []

    async def save(self, record: dict) -> None:
        self.saved.append(record)


def _all_tools() -> list[ToolDefinition]:
    return [
        ToolDefinition(name=name, description=f"tool {name}", input_schema={"type": "object"})
        for name in ALL_TOOLS
    ]


def _make_agent(
    llm: FakeLLM, sink: RecordingSink | None = None
) -> tuple[InventoryAgent, FakeGateway, RecordingSink]:
    sink = sink or RecordingSink()
    gateway = FakeGateway(_all_tools(), INVENTORY_DATA)
    agent = InventoryAgent(llm=llm, gateway=gateway, history=sink, max_iterations=3, max_tokens=128)
    return agent, gateway, sink


@pytest.mark.asyncio
async def test_read_only_user_gets_no_write_tools():
    llm = FakeLLM([text_response("Final answer")])
    agent, _, _ = _make_agent(llm)
    ctx = AgentContext(user_id="u1", role="viewer", can_write=False)
    await agent.run("What is low?", ctx)
    tool_names = {tool.name for tool in (llm.last_tools or [])}
    assert tool_names == set(READ_TOOLS)
    assert "update_cell" not in tool_names


@pytest.mark.asyncio
async def test_operator_gets_write_tools():
    llm = FakeLLM([text_response("Final answer")])
    agent, _, _ = _make_agent(llm)
    ctx = AgentContext(user_id="u1", role="operator", can_write=True)
    await agent.run("Update stock", ctx)
    tool_names = {tool.name for tool in (llm.last_tools or [])}
    assert "update_cell" in tool_names


@pytest.mark.asyncio
async def test_agent_calls_tools_then_answers():
    llm = FakeLLM(
        [tool_call_response("search_sheet", {"query": "bolt"}), text_response("Found 1 item")]
    )
    agent, gateway, sink = _make_agent(llm)
    ctx = AgentContext(user_id="u1", role="viewer", can_write=False)
    result = await agent.run("Find bolt", ctx)

    assert gateway.calls == [("search_sheet", {"query": "bolt"})]
    assert result.tool_calls_used == 1
    assert result.content == "Found 1 item"
    assert result.risk_flags == []
    assert len(sink.saved) == 1
    assert sink.saved[0]["agent_name"] == "inventory"
    assert sink.saved[0]["query"] == "Find bolt"


@pytest.mark.asyncio
async def test_agent_stops_at_iteration_cap():
    llm = FakeLLM([tool_call_response("search_sheet", {"query": "x"})] * 5)
    agent, gateway, _ = _make_agent(llm, RecordingSink())
    ctx = AgentContext(user_id="u1", role="viewer", can_write=False)
    result = await agent.run("Loop?", ctx)
    assert "could not complete" in result.content
    assert len(gateway.calls) == 3  # max_iterations=3


@pytest.mark.asyncio
async def test_risk_flag_extraction():
    assert _extract_risk_flags("3 items are low-stock and one stockout") == [
        "low-stock",
        "stockout",
    ]
    assert _extract_risk_flags("all good") == []


@pytest.mark.asyncio
async def test_system_prompt_respects_permissions():
    agent, _, _ = _make_agent(FakeLLM([text_response("ok")]))
    assert "READ-ONLY" in agent.system_prompt(can_write=False)
    assert "authorized to UPDATE" in agent.system_prompt(can_write=True)
