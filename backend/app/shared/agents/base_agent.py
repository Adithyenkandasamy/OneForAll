"""Agent contracts: context, result, and the Agent protocol.

Every business agent (inventory, procurement, ...) implements ``Agent``.
The runner in ``app/shared/agents/runner.py`` executes it; the HTTP layer
exposes it. This is the single extension point for new AI services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class AgentContext:
    user_id: str
    role: str
    can_write: bool = False
    conversation_id: str | None = None


@dataclass(frozen=True)
class AgentResult:
    content: str
    tool_calls_used: int = 0
    risk_flags: list[str] = field(default_factory=list)
    model: str = ""
    sources: list[str] = field(default_factory=list)


class Agent(Protocol):
    name: str
    description: str

    def system_prompt(self, *, can_write: bool = False) -> str: ...

    def tool_allowlist(self, *, can_write: bool = False) -> list[str]: ...

    async def run(self, query: str, ctx: AgentContext) -> AgentResult: ...
