"""Scripted fake LLM for deterministic agent tests."""

from __future__ import annotations

from typing import Any

from app.shared.llm.base import LLMResponse, ToolCall


class FakeLLM:
    """Returns the next scripted response on each call."""

    def __init__(self, script: list[LLMResponse]) -> None:
        self.script = list(script)
        self.calls: list[dict[str, Any]] = []
        self.last_tools: list[Any] | None = None

    async def complete(self, *, messages, tools=None, max_tokens=1024, temperature=0.1):
        self.calls.append({"messages": messages, "tools": tools})
        self.last_tools = tools
        if not self.script:
            return LLMResponse(content="no scripted response", model="fake-llm")
        return self.script.pop(0)


def tool_call_response(
    name: str, arguments: dict[str, Any], *, tool_call_id: str = "call_1"
) -> LLMResponse:
    return LLMResponse(
        content="",
        tool_calls=[ToolCall(id=tool_call_id, name=name, arguments=arguments)],
        model="fake-llm",
    )


def text_response(content: str) -> LLMResponse:
    return LLMResponse(content=content, model="fake-llm")
