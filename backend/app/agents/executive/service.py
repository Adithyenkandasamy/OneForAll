"""Executive Orchestrator service layer.

Connects to inventory MCP tools for real data access.
Prevents hallucination by requiring tool usage for factual claims.
"""

from __future__ import annotations

import json

from app.core.logging import get_logger
from app.core.config import settings
from app.agents.inventory.mcp_tools import SheetsMcpGateway
from app.shared.llm.groq import GroqProvider
from app.shared.llm.base import ToolDefinition

logger = get_logger(__name__)

SYSTEM_PROMPT = """\
You are the OneForAll Central AI Orchestrator for a manufacturing company.

CRITICAL RULES - READ CAREFULLY:
1. NEVER, EVER make up or fabricate ANY data. Every single number, product name, \
stock level, supplier name, or metric MUST come from a tool call result.
2. You have NO knowledge of this company's inventory. You MUST use tools to \
get any information.
3. If a tool call fails or returns an error, say "I cannot retrieve that data \
right now" - do NOT guess.
4. When asked about inventory, ALWAYS call get_sheet_data or search_materials first.
5. When asked about stock levels, ALWAYS call get_low_stock or query_inventory.
6. If you don't have a tool for something, say "I don't have access to that data" \
instead of making something up.
7. Never provide percentages, dollar values, or metrics unless they come directly \
from a tool result.
8. Address the user professionally. You are an AI assistant with real-time \
access to factory inventory data through MCP tools.
"""


class ExecutiveService:
    def __init__(self) -> None:
        self._gateway = SheetsMcpGateway()
        self._llm = GroqProvider(api_key=settings.groq_central_api_key)

    async def answer(
        self, query: str, *, user_id: str, role: str, conversation_id: str | None
    ) -> dict:
        from app.shared.mcp import client as mcp_client

        # Get available tools from MCP server
        try:
            server = self._gateway._resolve_server()
            tools = await mcp_client.list_tools(server)
        except Exception as exc:
            logger.warning("Failed to list MCP tools", extra={"error": str(exc)})
            tools = []

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]

        tool_calls_used = 0
        max_iterations = 10

        for _ in range(max_iterations):
            response = await self._llm.complete(
                messages=messages,
                tools=tools if tools else None,
                max_tokens=2048,
                temperature=0.1,
            )

            # If no tool calls, return the final answer
            if not response.tool_calls:
                return {
                    "content": response.content or "No content returned.",
                    "tool_calls_used": tool_calls_used,
                    "model": response.model or settings.groq_model,
                    "risk_flags": [],
                    "conversation_id": conversation_id,
                }

            # Execute tool calls
            messages.append({
                "role": "assistant",
                "content": response.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.name,
                            "arguments": json.dumps(call.arguments) if isinstance(call.arguments, dict) else call.arguments,
                        },
                    }
                    for call in response.tool_calls
                ],
            })

            for call in response.tool_calls:
                tool_calls_used += 1
                try:
                    args = call.arguments
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except json.JSONDecodeError:
                            args = {}
                    result = await self._gateway.call_tool(call.name, args)
                    result_text = str(result)
                except Exception as exc:
                    logger.warning("Tool call failed", extra={"tool": call.name, "error": str(exc)})
                    result_text = f"ERROR: Tool '{call.name}' failed: {exc}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result_text,
                })

        return {
            "content": "I could not complete the analysis within the allowed iterations.",
            "tool_calls_used": tool_calls_used,
            "model": settings.groq_model,
            "risk_flags": [],
            "conversation_id": conversation_id,
        }
