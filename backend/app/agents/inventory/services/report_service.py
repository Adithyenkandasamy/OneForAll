"""Report Service — structured report generation.

Generates inventory summary reports in JSON format.
Excel and PDF generation can be added as future extensions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.agents.inventory.services.rule_engine import MaterialAnalysis
from app.agents.inventory.services.health_engine import InventoryHealth


@dataclass(frozen=True)
class InventoryReport:
    """Structured inventory report output."""

    report_type: str   # "summary" | "daily" | "weekly" | "monthly"
    generated_at: str
    health: dict
    total_materials: int
    high_risk_materials: list[dict]
    reorder_list: list[dict]
    stockout_list: list[dict]
    overstock_list: list[dict]


class ReportService:
    """Generates structured reports from engine outputs."""

    def generate_summary(
        self,
        analyses: list[MaterialAnalysis],
        health: InventoryHealth,
    ) -> InventoryReport:
        return InventoryReport(
            report_type="summary",
            generated_at=datetime.now(timezone.utc).isoformat(),
            health={
                "score": health.health_score,
                "total": health.total_materials,
                "safe": health.safe_count,
                "high_risk": health.high_risk_count,
                "medium_risk": health.medium_risk_count,
                "critical": health.critical_count,
            },
            total_materials=health.total_materials,
            high_risk_materials=[
                self._to_report_row(a) for a in analyses if a.risk_level == "HIGH"
            ],
            reorder_list=[
                self._to_report_row(a) for a in analyses if a.reorder_required
            ],
            stockout_list=[
                self._to_report_row(a) for a in analyses if a.stockout_detected
            ],
            overstock_list=[
                self._to_report_row(a) for a in analyses if a.overstock_detected
            ],
        )

    @staticmethod
    def _to_report_row(a: MaterialAnalysis) -> dict:
        return {
            "sku": a.sku,
            "name": a.name,
            "current_stock": a.current_stock,
            "minimum_stock": a.minimum_stock,
            "daily_consumption": a.daily_consumption,
            "days_remaining": a.days_remaining,
            "risk_level": a.risk_level,
            "priority": a.priority,
            "supplier": a.supplier,
            "reorder_required": a.reorder_required,
        }
