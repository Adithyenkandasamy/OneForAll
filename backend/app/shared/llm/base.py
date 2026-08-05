"""LLM provider abstraction.

The rest of the platform depends only on these types, never on the Groq SDK.
Swap providers by implementing ``LLMProvider`` and registering it in the
container.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ToolDefinition:
    """A tool exposed to the LLM (mirrors an MCP tool)."""

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LLMResponse:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str = ""


class LLMProvider(Protocol):
    async def complete(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[ToolDefinition] | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.1,
    ) -> LLMResponse:
        """Run a chat completion. Returns content and/or tool calls."""
        ...
