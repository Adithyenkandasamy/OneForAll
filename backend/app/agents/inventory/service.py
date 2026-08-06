"""Inventory use-cases: answer, search, update, health, analytics, dashboard, report.

The service layer orchestrates the data flow:
  MCP Gateway → Rule Engine → Health Engine → Analytics Engine → AI Agent

Business logic is NEVER delegated to the LLM. The AI only explains
pre-computed structured results.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from app.agents.inventory.exceptions import InvalidUpdateError, UnauthorizedToolError
from app.agents.inventory.mcp_tools import SheetsMcpGateway
from app.agents.inventory.models import InventoryItem
from app.agents.inventory.schemas import InventoryItemDTO, MaterialAnalysisDTO
from app.agents.inventory.services.analytics_engine import AnalyticsEngine
from app.agents.inventory.services.cache_service import CacheService
from app.agents.inventory.services.health_engine import HealthEngine
from app.agents.inventory.services.rule_engine import RuleEngine
from app.agents.inventory.services.report_service import ReportService
from app.core.logging import get_logger
from app.services.notification_service import NotificationService

logger = get_logger(__name__)

WRITE_ROLES = {"operator", "admin"}
WRITABLE_COLUMNS = ("qty", "quantity", "stock", "name", "reorder", "status",
                    "Current Stock", "Minimum Stock", "AI Risk Level",
                    "current_stock", "ai_risk_level", "minimum_stock")


class InventoryService:
    def __init__(
        self,
        agent: object,
        gateway: SheetsMcpGateway,
        *,
        notification_service: NotificationService | None = None,
        rule_engine: RuleEngine | None = None,
        health_engine: HealthEngine | None = None,
        analytics_engine: AnalyticsEngine | None = None,
        report_service: ReportService | None = None,
        cache: CacheService | None = None,
    ) -> None:
        self._agent = agent
        self._gateway = gateway
        self._notification_service = notification_service
        self._rule_engine = rule_engine or RuleEngine()
        self._health_engine = health_engine or HealthEngine()
        self._analytics_engine = analytics_engine or AnalyticsEngine()
        self._report_service = report_service or ReportService()
        self._cache = cache or CacheService()

    # ── Raw MCP data access ──

    async def _fetch_all_rows(self) -> list[dict]:
        """Fetch all rows from the Google Sheet via MCP, with caching."""
        cached = self._cache.get()
        if cached is not None:
            return cached

        result = await self._gateway.call_tool("search_materials", {"query": "MAT"})
        if isinstance(result, dict):
            rows = [result]
        elif isinstance(result, list):
            rows = result
        else:
            rows = []

        self._cache.set(rows)
        return rows

    async def _create_risk_notifications(self, analyses: list, user_id: str) -> None:
        """Create notifications for HIGH risk materials."""
        if self._notification_service is None:
            return

        high_risk = [a for a in analyses if a.risk_level == "HIGH"]
        if not high_risk:
            return

        for material in high_risk:
            kind = "stockout" if material.stockout_detected else "low_stock"
            title = f"Stock Alert: {material.name} ({material.sku})"
            body = (
                f"Current stock: {material.current_stock}, "
                f"Minimum: {material.minimum_stock}. "
                f"{'STOCKOUT DETECTED!' if material.stockout_detected else 'Below minimum stock level.'}"
            )
            payload = {"link": "/inventory", "sku": material.sku, "risk_level": material.risk_level}

            await self._notification_service.create(
                user_id=user_id,
                kind=kind,
                title=title,
                body=body,
                payload=payload,
            )

    # ── Existing endpoints (preserved) ──

    async def answer(
        self, query: str, *, user_id: str, role: str, conversation_id: str | None
    ) -> dict:
        """AI-powered answer with pre-computed structured context."""
        from app.shared.agents.base_agent import AgentContext

        # Step 1: Fetch data and run deterministic engines
        rows = await self._fetch_all_rows()
        analyses = self._rule_engine.analyze_all(rows)
        health = self._health_engine.compute(analyses)

        # Step 2: Build structured context for the AI
        structured_context = {
            "health_score": health.health_score,
            "total_materials": health.total_materials,
            "high_risk_count": health.high_risk_count,
            "critical_count": health.critical_count,
            "stockout_count": health.stockout_count,
            "materials": [asdict(a) for a in analyses],
        }

        # Step 3: Prefix the query with structured data so the AI explains it
        enriched_query = (
            f"[STRUCTURED INVENTORY DATA]\n"
            f"{json.dumps(structured_context, indent=2)}\n\n"
            f"[USER QUERY]\n{query}"
        )

        can_write = role in WRITE_ROLES
        ctx = AgentContext(
            user_id=user_id, role=role, can_write=can_write, conversation_id=conversation_id
        )
        result = await self._agent.run(enriched_query, ctx)

        # Step 4: Publish domain event to the Internal Event Bus
        await bus.publish(
            "inventory:analyzed", 
            {"analyses": analyses, "user_id": user_id}
        )

        # Step 5: Create notifications for high-risk materials
        await self._create_risk_notifications(analyses, user_id)

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
        self._cache.invalidate()  # Force re-fetch on next read
        logger.info(
            "Inventory updated",
            extra={"sku": sku, "column": column, "value": value, "result": str(result)},
        )
        return {"message": str(result), "sku": sku, "column": column, "value": value}

    # ── New endpoints (Phase 3) ──

    async def get_health(self) -> dict:
        """Return deterministic inventory health snapshot."""
        rows = await self._fetch_all_rows()
        analyses = self._rule_engine.analyze_all(rows)
        health = self._health_engine.compute(analyses)
        return asdict(health)

    async def get_analytics(self) -> dict:
        """Return structured analytics snapshot."""
        rows = await self._fetch_all_rows()
        analyses = self._rule_engine.analyze_all(rows)
        snapshot = self._analytics_engine.compute(analyses)
        return asdict(snapshot)

    async def get_dashboard(self) -> dict:
        """Combined dashboard: health + top critical + supplier stats."""
        rows = await self._fetch_all_rows()
        analyses = self._rule_engine.analyze_all(rows)
        health = self._health_engine.compute(analyses)
        analytics = self._analytics_engine.compute(analyses)

        # Top critical materials for the dashboard
        critical = sorted(
            [a for a in analyses if a.risk_level in ("HIGH", "MEDIUM")],
            key=lambda a: a.days_remaining or 0,
        )[:5]

        return {
            "health": asdict(health),
            "top_critical": [asdict(a) for a in critical],
            "risk_distribution": health.risk_distribution,
            "supplier_stats": analytics.supplier_stats,
        }

    async def generate_report(self, report_type: str = "summary") -> dict:
        """Generate a structured inventory report."""
        rows = await self._fetch_all_rows()
        analyses = self._rule_engine.analyze_all(rows)
        health = self._health_engine.compute(analyses)
        report = self._report_service.generate_summary(analyses, health)
        return asdict(report)

    async def get_enriched_materials(self) -> list[dict]:
        """Return all materials with deterministic analysis applied."""
        rows = await self._fetch_all_rows()
        analyses = self._rule_engine.analyze_all(rows)
        return [asdict(a) for a in analyses]
