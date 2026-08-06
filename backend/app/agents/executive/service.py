"""Executive Orchestrator service layer.

Connects to inventory MCP tools for real data access.
Prevents hallucination by requiring tool usage for factual claims.
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.core.config import settings
from app.agents.inventory.mcp_tools import SheetsMcpGateway

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

TOOLS_DESCRIPTION = """\
You have access to these inventory tools:
- get_sheet_data: Get all inventory data
- search_materials: Search by keyword across all columns
- get_low_stock: Get materials below reorder point
- get_supplier_stats: Get materials per supplier
- query_inventory: Flexible query with filters
- get_material: Get single material by ID
- get_columns: List column names
"""


class ExecutiveService:
    def __init__(self) -> None:
        self._gateway = SheetsMcpGateway()

    async def answer(
        self, query: str, *, user_id: str, role: str, conversation_id: str | None
    ) -> dict:
        from groq import AsyncGroq
        from app.shared.mcp import client as mcp_client

        client = AsyncGroq(api_key=settings.groq_central_api_key)

        # Get available tools from MCP server
        try:
            server = self._gateway._resolve_server()
            tools = await mcp_client.list_tools(server)
        except Exception as exc:
            logger.warning("Failed to list MCP tools", extra={"error": str(exc)})
            tools = []

        # Convert tools to Groq function format
        groq_tools = []
        for tool in tools:
            groq_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            })

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + TOOLS_DESCRIPTION},
            {"role": "user", "content": query},
        ]

        tool_calls_used = 0
        max_iterations = 10

        for _ in range(max_iterations):
            response = await client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                tools=groq_tools if groq_tools else None,
                max_tokens=2048,
                temperature=0.1,
            )

            choice = response.choices[0]
            message = choice.message

            # If no tool calls, return the final answer
            if not message.tool_calls:
                content = message.content or "No content returned."
                return {
                    "content": content,
                    "tool_calls_used": tool_calls_used,
                    "model": settings.groq_model,
                    "risk_flags": [],
                    "conversation_id": conversation_id,
                }

            # Execute tool calls
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in message.tool_calls
                ],
            })

            for tc in message.tool_calls:
                tool_calls_used += 1
                tool_name = tc.function.name
                import json
                try:
                    tool_args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                try:
                    result = await self._gateway.call_tool(tool_name, tool_args)
                    result_text = str(result)
                except Exception as exc:
                    logger.warning("Tool call failed", extra={"tool": tool_name, "error": str(exc)})
                    result_text = f"ERROR: Tool '{tool_name}' failed: {exc}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_text,
                })

        return {
            "content": "I could not complete the analysis within the allowed iterations.",
            "tool_calls_used": tool_calls_used,
            "model": settings.groq_model,
            "risk_flags": [],
            "conversation_id": conversation_id,
        }
