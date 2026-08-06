"""Groq LLM provider (Llama 3.3 70B) implementing LLMProvider."""

from __future__ import annotations

import json
from typing import Any

import groq

from app.core.config import settings
from app.core.logging import get_logger
from app.shared.llm.base import LLMProvider, LLMResponse, ToolCall, ToolDefinition

logger = get_logger(__name__)


class GroqProvider(LLMProvider):
    def __init__(self, *, api_key: str | None = None, model: str | None = None) -> None:
        self._client = groq.AsyncGroq(api_key=api_key or settings.GROQ_API_KEY_INVENTORY)
        self._model = model or settings.groq_model

    async def complete(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[ToolDefinition] | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.1,
    ) -> LLMResponse:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema,
                    },
                }
                for tool in tools
            ]

        response = await self._client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        tool_calls = [
            ToolCall(
                id=call.id,
                name=call.function.name,
                arguments=_parse_arguments(call.function.arguments),
            )
            for call in (message.tool_calls or [])
        ]
        return LLMResponse(
            content=message.content or "",
            tool_calls=tool_calls,
            model=self._model,
        )


def _parse_arguments(raw: Any) -> dict[str, Any]:
    """Groq returns tool arguments as a JSON string; some SDKs give a dict."""
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}
