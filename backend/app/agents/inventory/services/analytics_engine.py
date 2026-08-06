"""Analytics Engine — structured inventory analytics.

Produces fast/slow movers, dead stock, supplier stats, ABC analysis,
and top critical materials from Rule Engine output.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from app.agents.inventory.services.rule_engine import MaterialAnalysis


@dataclass(frozen=True)
class AnalyticsSnapshot:
    """Structured analytics result."""

    fast_moving: list[dict]        # sorted by consumption DESC
    slow_moving: list[dict]        # sorted by consumption ASC (non-zero)
    dead_stock: list[dict]         # zero consumption
    supplier_stats: dict[str, int]
    top_critical: list[dict]       # sorted by days_remaining ASC
    abc_analysis: dict[str, list[dict]]  # A / B / C buckets
    consumption_summary: dict[str, int]  # HIGH / MEDIUM / LOW / ZERO counts


class AnalyticsEngine:
    """Stateless analytics processor."""

    def compute(self, analyses: list[MaterialAnalysis]) -> AnalyticsSnapshot:
        return AnalyticsSnapshot(
            fast_moving=self._fast_moving(analyses),
            slow_moving=self._slow_moving(analyses),
            dead_stock=self._dead_stock(analyses),
            supplier_stats=self._supplier_stats(analyses),
            top_critical=self._top_critical(analyses),
            abc_analysis=self._abc_analysis(analyses),
            consumption_summary=self._consumption_summary(analyses),
        )

    def _fast_moving(self, analyses: list[MaterialAnalysis], limit: int = 10) -> list[dict]:
        moving = [a for a in analyses if a.daily_consumption > 0]
        moving.sort(key=lambda a: a.daily_consumption, reverse=True)
        return [self._to_summary(a) for a in moving[:limit]]

    def _slow_moving(self, analyses: list[MaterialAnalysis], limit: int = 10) -> list[dict]:
        moving = [a for a in analyses if a.daily_consumption > 0]
        moving.sort(key=lambda a: a.daily_consumption)
        return [self._to_summary(a) for a in moving[:limit]]

    def _dead_stock(self, analyses: list[MaterialAnalysis]) -> list[dict]:
        dead = [a for a in analyses if a.daily_consumption == 0 and a.current_stock > 0]
        return [self._to_summary(a) for a in dead]

    def _supplier_stats(self, analyses: list[MaterialAnalysis]) -> dict[str, int]:
        return dict(Counter(a.supplier for a in analyses))

    def _top_critical(self, analyses: list[MaterialAnalysis], limit: int = 10) -> list[dict]:
        critical = [a for a in analyses if a.days_remaining is not None and a.risk_level in ("HIGH", "MEDIUM")]
        critical.sort(key=lambda a: a.days_remaining or 0)
        return [self._to_summary(a) for a in critical[:limit]]

    def _abc_analysis(self, analyses: list[MaterialAnalysis]) -> dict[str, list[dict]]:
        """ABC classification by consumption volume (qty × daily_consumption).

        A = top 20% contribution, B = next 30%, C = remaining 50%.
        """
        scored = [(a, a.current_stock * max(a.daily_consumption, 1)) for a in analyses]
        scored.sort(key=lambda x: x[1], reverse=True)
        total_value = sum(s for _, s in scored) or 1

        buckets: dict[str, list[dict]] = {"A": [], "B": [], "C": []}
        cumulative = 0.0
        for analysis, value in scored:
            cumulative += value / total_value
            if cumulative <= 0.20:
                buckets["A"].append(self._to_summary(analysis))
            elif cumulative <= 0.50:
                buckets["B"].append(self._to_summary(analysis))
            else:
                buckets["C"].append(self._to_summary(analysis))
        return buckets

    def _consumption_summary(self, analyses: list[MaterialAnalysis]) -> dict[str, int]:
        return dict(Counter(a.consumption_status for a in analyses))

    @staticmethod
    def _to_summary(a: MaterialAnalysis) -> dict:
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
        }
