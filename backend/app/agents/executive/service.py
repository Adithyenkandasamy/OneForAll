"""Executive Orchestrator service layer.

Connects to domain services (e.g. InventoryService) instead of raw DBs/MCPs.
Adheres to Modular Monolith boundaries.
"""

from __future__ import annotations

import json
from inspect import iscoroutinefunction

from app.core.logging import get_logger
from app.core.config import settings
from app.shared.llm.groq import GroqProvider
from app.shared.llm.base import ToolDefinition

from app.agents.inventory.service import InventoryService
from app.agents.inventory.mcp_tools import SheetsMcpGateway
from app.agents.quality.services.service import QualityService

logger = get_logger(__name__)

SYSTEM_PROMPT = """\
You are Orvixo, the Central Executive AI Orchestrator for this Manufacturing Intelligence Platform.

CRITICAL RULES:
1. NEVER fabricate data. All metrics, health scores, and stock levels MUST come from your tools.
2. You do not calculate risk, days remaining, or health yourself. The backend rule engines pre-compute these. Your job is to EXPLAIN them intelligently.
3. Be concise, strategic, and professional. Do not just dump raw JSON arrays back to the user. Synthesize the data into actionable business intelligence.
4. If the user asks about the overall status, query the dashboard or health tools, then provide a high-level executive summary. Only list specific materials if they are critical or requested.
5. If the user asks about machine health, CNC node telemetry, or manufacturing quality, query the `get_quality_monitoring` tool to evaluate physical asset risk!
6. FORMATTING: Do NOT use markdown formatting like **bold** or *italic* or # headers. Write in plain text only. Use simple sentences, bullet points, or numbered lists. No special characters or symbols.
"""

class ExecutiveService:
    def __init__(self) -> None:
        self._llm = GroqProvider(api_key=settings.groq_central_api_key)
        # In a true modular monolith, we access other bounding contexts through their service layer
        # Eventually we would inject this via a Dependency Container
        self._inventory_service = InventoryService(
            agent=None,  # Executive doesn't use the inventory local agent
            gateway=SheetsMcpGateway()
        )
        self._quality_service = QualityService()

    def _get_domain_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="get_inventory_health",
                description="Get the current overall inventory health score and risk distribution.",
                input_schema={"type": "object", "properties": {}}
            ),
            ToolDefinition(
                name="get_inventory_dashboard",
                description="Get the top critical materials, supplier stats, and health overview.",
                input_schema={"type": "object", "properties": {}}
            ),
            ToolDefinition(
                name="get_inventory_analytics",
                description="Get detailed ABC analysis, dead stock, and fast/slow movers.",
                input_schema={"type": "object", "properties": {}}
            ),
            ToolDefinition(
                name="search_inventory_materials",
                description="Search for specific materials or get all materials if query is empty.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search term (e.g. MAT). Leave empty for all."}
                    }
                }
            ),
            ToolDefinition(
                name="get_quality_monitoring",
                description="Get the live Quality Monitoring dashboard state, featuring real-time CNC machine IoT telemetry (Vibration, Temperature) and Health/Quality metrics.",
                input_schema={"type": "object", "properties": {}}
            )
        ]

    async def _execute_tool(self, name: str, args: dict) -> str:
        try:
            if name == "get_inventory_health":
                res = await self._inventory_service.get_health()
            elif name == "get_inventory_dashboard":
                res = await self._inventory_service.get_dashboard()
            elif name == "get_inventory_analytics":
                res = await self._inventory_service.get_analytics()
            elif name == "search_inventory_materials":
                q = args.get("query", "MAT")
                # Need to use the raw enriched fetch if they just want everything
                if not q:
                    res = await self._inventory_service.get_enriched_materials()
                else:
                    res = await self._inventory_service.get_enriched_materials()
                    # simplistic filter
                    q = q.lower()
                    res = [m for m in res if q in str(m.get("material_id", "")).lower() or q in str(m.get("material", "")).lower()]
            elif name == "get_quality_monitoring":
                res = await self._quality_service.get_dashboard_state()
            else:
                return f"ERROR: Unknown tool {name}"
            
            return json.dumps(res, default=str)
        except Exception as e:
            logger.error("Domain tool execution failed", extra={"tool": name, "error": str(e)})
            return f"ERROR executing {name}: {str(e)}"

    async def answer(
        self, query: str, *, user_id: str, role: str, conversation_id: str | None
    ) -> dict:
        
        tools = self._get_domain_tools()

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]

        tool_calls_used = 0
        max_iterations = 6

        for _ in range(max_iterations):
            response = await self._llm.complete(
                messages=messages,
                tools=tools,
                max_tokens=2048,
                temperature=0.3,
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

            # Add AI's function dispatch to history
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

            # Execute tools
            for call in response.tool_calls:
                tool_calls_used += 1
                args = call.arguments
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {}
                
                result_text = await self._execute_tool(call.name, args)

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
