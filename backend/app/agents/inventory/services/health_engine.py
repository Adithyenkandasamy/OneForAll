"""Health Engine — aggregate inventory health metrics.

Consumes Rule Engine output and produces a single health snapshot
suitable for dashboards and executive summaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.agents.inventory.services.rule_engine import MaterialAnalysis


@dataclass(frozen=True)
class InventoryHealth:
    """Aggregated health snapshot across all materials."""

    total_materials: int
    safe_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    overstock_count: int
    stockout_count: int
    critical_count: int
    reorder_count: int
    health_score: float  # 0.0–100.0
    risk_distribution: dict[str, int] = field(default_factory=dict)


class HealthEngine:
    """Stateless aggregator. Takes MaterialAnalysis list, returns InventoryHealth."""

    def compute(self, analyses: list[MaterialAnalysis]) -> InventoryHealth:
        total = len(analyses)
        if total == 0:
            return InventoryHealth(
                total_materials=0,
                safe_count=0,
                high_risk_count=0,
                medium_risk_count=0,
                low_risk_count=0,
                overstock_count=0,
                stockout_count=0,
                critical_count=0,
                reorder_count=0,
                health_score=100.0,
                risk_distribution={"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            )

        high = sum(1 for a in analyses if a.risk_level == "HIGH")
        medium = sum(1 for a in analyses if a.risk_level == "MEDIUM")
        low = sum(1 for a in analyses if a.risk_level == "LOW")
        overstock = sum(1 for a in analyses if a.overstock_detected)
        stockout = sum(1 for a in analyses if a.stockout_detected)
        critical = sum(1 for a in analyses if a.priority == "CRITICAL")
        reorder = sum(1 for a in analyses if a.reorder_required)
        safe = total - high - medium

        # Health score: percentage of materials that are NOT high-risk
        health_score = round(((total - high) / total) * 100, 1) if total > 0 else 100.0

        return InventoryHealth(
            total_materials=total,
            safe_count=max(safe, 0),
            high_risk_count=high,
            medium_risk_count=medium,
            low_risk_count=low,
            overstock_count=overstock,
            stockout_count=stockout,
            critical_count=critical,
            reorder_count=reorder,
            health_score=health_score,
            risk_distribution={"HIGH": high, "MEDIUM": medium, "LOW": low},
        )
