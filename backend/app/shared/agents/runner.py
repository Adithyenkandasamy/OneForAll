"""Tool-calling orchestration loop shared by every agent.

Loop: system prompt + tools -> LLM -> execute tool calls via the injected
gateway -> feed results back -> repeat until the LLM returns a final
answer or the iteration cap is reached.

The agent NEVER touches MCP directly — it only sees ToolDefinitions and an
``execute_tool`` callable. This is what makes agents portable to any data
source.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from app.core.exceptions import AppError, LlmUnavailableError, McpUnavailableError
from app.core.logging import get_logger
from app.shared.llm.base import LLMProvider, ToolCall, ToolDefinition

logger = get_logger(__name__)

ExecuteTool = Callable[[str, dict[str, Any]], Awaitable[str]]


class AgentRunner:
    def __init__(
        self,
        *,
        llm: LLMProvider,
        tools: list[ToolDefinition],
        execute_tool: ExecuteTool,
        max_iterations: int = 5,
        max_tokens: int = 1024,
    ) -> None:
        self._llm = llm
        self._tools = tools
        self._execute_tool = execute_tool
        self._max_iterations = max_iterations
        self._max_tokens = max_tokens

    async def run(self, *, system_prompt: str, query: str) -> tuple[str, int, str]:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        tool_calls_used = 0
        model = ""

        for _ in range(self._max_iterations):
            try:
                response = await self._llm.complete(
                    messages=messages, tools=self._tools, max_tokens=self._max_tokens
                )
            except Exception as exc:
                logger.warning("LLM call failed", extra={"error": str(exc)})
                raise LlmUnavailableError("AI provider unavailable") from exc

            model = response.model or model

            if not response.tool_calls:
                return response.content, tool_calls_used, model

            messages.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {"name": call.name, "arguments": _json_args(call)},
                        }
                        for call in response.tool_calls
                    ],
                }
            )
            for call in response.tool_calls:
                tool_calls_used += 1
                result_text = await self._run_tool(call)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result_text,
                    }
                )

        return (
            "I could not complete the analysis within the allowed iterations.",
            tool_calls_used,
            model,
        )

    async def _run_tool(self, call: ToolCall) -> str:
        try:
            result = await self._execute_tool(call.name, call.arguments)
            return str(result)
        except McpUnavailableError:
            raise
        except AppError as exc:
            logger.warning("Agent tool failed", extra={"tool": call.name, "error": exc.message})
            return f"ERROR: {exc.message}"
        except Exception as exc:
            logger.warning("Agent tool failed", extra={"tool": call.name, "error": str(exc)})
            return f"ERROR: {exc}"


def _json_args(call: ToolCall) -> str:
    import json

    return json.dumps(call.arguments or {})
