"""Inventory AI agent — policy and orchestration for the inventory domain.

Implements the shared ``Agent`` protocol. Responsibilities:
- Decide the system prompt and tool allow-list for the caller's role.
- Run the tool-calling loop via ``AgentRunner``.
- Persist the analysis through the injected ``HistorySink``.

The agent holds NO knowledge of Google Sheets internals; it only sees the
``McpGateway`` port and tool definitions.
"""

from __future__ import annotations

from app.agents.inventory.mcp_tools import ALL_TOOLS, READ_TOOLS, SheetsMcpGateway
from app.agents.inventory.ports import HistorySink
from app.agents.inventory.prompt import build_system_prompt
from app.core.config import settings
from app.core.logging import get_logger
from app.shared.agents.base_agent import AgentContext, AgentResult
from app.shared.agents.runner import AgentRunner
from app.shared.llm.base import LLMProvider, ToolDefinition

logger = get_logger(__name__)

_RISK_KEYWORDS = ("stockout", "low-stock", "low stock", "overstock", "data-missing", "expiring")


class InventoryAgent:
    name = "inventory"
    description = "Analyzes factory inventory from Google Sheets: search, risk, and reorder advice."

    def __init__(
        self,
        *,
        llm: LLMProvider,
        gateway: SheetsMcpGateway,
        history: HistorySink,
        max_iterations: int | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self._llm = llm
        self._gateway = gateway
        self._history = history
        self._max_iterations = max_iterations or settings.llm_max_iterations
        self._max_tokens = max_tokens or settings.llm_max_tokens

    def system_prompt(self, *, can_write: bool = False) -> str:
        return build_system_prompt(can_write=can_write)

    def tool_allowlist(self, *, can_write: bool = False) -> list[str]:
        return list(ALL_TOOLS) if can_write else list(READ_TOOLS)

    async def run(self, query: str, ctx: AgentContext) -> AgentResult:
        can_write = ctx.can_write
        tools = await self._available_tools(can_write=can_write)
        runner = AgentRunner(
            llm=self._llm,
            tools=tools,
            execute_tool=self._gateway.call_tool,
            max_iterations=self._max_iterations,
            max_tokens=self._max_tokens,
        )
        content, tool_calls_used, model = await runner.run(
            system_prompt=self.system_prompt(can_write=can_write), query=query
        )
        risk_flags = _extract_risk_flags(content)
        await self._history.save(
            {
                "user_id": ctx.user_id,
                "agent_name": self.name,
                "query": query,
                "response": content,
                "model": model,
                "tool_calls_used": tool_calls_used,
                "risk_flags": risk_flags,
            }
        )
        return AgentResult(
            content=content,
            tool_calls_used=tool_calls_used,
            risk_flags=risk_flags,
            model=model,
        )

    async def _available_tools(self, *, can_write: bool) -> list[ToolDefinition]:
        allowed = set(self.tool_allowlist(can_write=can_write))
        try:
            server_tools = await self._gateway.list_tools()
        except Exception as exc:
            logger.warning("Unable to list MCP tools", extra={"error": str(exc)})
            return []
        return [tool for tool in server_tools if tool.name.split(".", 1)[-1] in allowed]


def _extract_risk_flags(content: str) -> list[str]:
    lowered = content.lower()
    return sorted(keyword for keyword in _RISK_KEYWORDS if keyword in lowered)
