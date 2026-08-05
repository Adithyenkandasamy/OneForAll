"""Inventory use-cases: answer, search, and (authorized) update."""

from __future__ import annotations

from app.agents.inventory.exceptions import InvalidUpdateError, UnauthorizedToolError
from app.agents.inventory.mcp_tools import SheetsMcpGateway
from app.agents.inventory.models import InventoryItem
from app.agents.inventory.schemas import InventoryItemDTO
from app.core.logging import get_logger

logger = get_logger(__name__)

WRITE_ROLES = {"operator", "admin"}
WRITABLE_COLUMNS = ("qty", "quantity", "stock", "name", "reorder", "status")


class InventoryService:
    def __init__(self, agent: object, gateway: SheetsMcpGateway) -> None:
        self._agent = agent
        self._gateway = gateway

    async def answer(
        self, query: str, *, user_id: str, role: str, conversation_id: str | None
    ) -> dict:
        from app.shared.agents.base_agent import AgentContext

        can_write = role in WRITE_ROLES
        ctx = AgentContext(
            user_id=user_id, role=role, can_write=can_write, conversation_id=conversation_id
        )
        result = await self._agent.run(query, ctx)
        return {
            "content": result.content,
            "tool_calls_used": result.tool_calls_used,
            "model": result.model,
            "risk_flags": result.risk_flags,
            "conversation_id": conversation_id,
        }

    async def search(self, query: str, *, limit: int = 25) -> list[InventoryItemDTO]:
        result = await self._gateway.call_tool("search_materials", {"query": query})
        if isinstance(result, dict):
            rows = [result]
        elif isinstance(result, list):
            rows = result
        else:
            rows = []
        items = [InventoryItem.from_row(row) for row in rows[:limit]]
        return [InventoryItemDTO(**item.__dict__) for item in items]

    async def update(self, *, sku: str, column: str, value: str, role: str) -> dict:
        if role not in WRITE_ROLES:
            raise UnauthorizedToolError("Updating inventory requires operator or admin role")
        if column not in WRITABLE_COLUMNS:
            raise InvalidUpdateError(f"Column {column!r} is not writable")
        result = await self._gateway.call_tool(
            "update_cell", {"sku": sku, "column": column, "value": value}
        )
        logger.info(
            "Inventory updated",
            extra={"sku": sku, "column": column, "value": value, "result": str(result)},
        )
        return {"message": str(result), "sku": sku, "column": column, "value": value}
