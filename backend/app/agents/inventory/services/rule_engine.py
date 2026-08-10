"""Rule Engine — deterministic inventory risk and status calculations.

This service is the SINGLE SOURCE OF TRUTH for all business rules.
The LLM must NEVER calculate these values; they are always pre-computed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MaterialAnalysis:
    """Output of the Rule Engine for a single material row."""

    sku: str
    name: str
    category: str
    unit: str
    current_stock: int
    minimum_stock: int
    daily_consumption: int
    supplier: str

    # ── Computed fields ──
    risk_level: str          # HIGH | MEDIUM | LOW
    days_remaining: float | None  # None if consumption is 0
    reorder_required: bool
    stockout_detected: bool
    overstock_detected: bool
    consumption_status: str  # HIGH | MEDIUM | LOW | ZERO
    priority: str            # CRITICAL | HIGH | MEDIUM | LOW


class RuleEngine:
    """Pure-function engine. No I/O, no side-effects, no LLM calls."""

    # ── Thresholds (configurable per-deployment) ──
    OVERSTOCK_MULTIPLIER: float = 3.0
    MEDIUM_RISK_MULTIPLIER: float = 1.5
    HIGH_CONSUMPTION_THRESHOLD: int = 30
    MEDIUM_CONSUMPTION_THRESHOLD: int = 10

    def analyze_material(self, row: dict[str, Any]) -> MaterialAnalysis:
        """Analyze a single material row from the Google Sheet."""
        # Support both normalized API fields and the human-readable headers
        # used by the OneForAll Google Sheet template.
        sku = str(row.get("material_id") or row.get("Material ID") or row.get("sku") or row.get("SKU") or "")
        name = str(row.get("material") or row.get("Material") or row.get("name") or row.get("Name") or "")
        category = str(row.get("category") or row.get("Category") or "Uncategorised")
        unit = str(row.get("unit") or row.get("Unit") or "")
        current_stock = self._to_int(
            row.get("current_stock") or row.get("Current Stock") or row.get("qty") or row.get("quantity") or 0
        )
        minimum_stock = self._to_int(
            row.get("minimum_stock") or row.get("Minimum Stock") or row.get("reorder") or row.get("min") or 0
        )
        daily_consumption = self._to_int(
            row.get("consumption") or row.get("daily_consumption") or row.get("Daily Consumption") or 0
        )
        supplier = str(row.get("supplier") or row.get("Supplier") or "Unknown")

        risk_level = self._compute_risk(current_stock, minimum_stock)
        days_remaining = self._compute_days_remaining(current_stock, daily_consumption)
        reorder_required = current_stock <= minimum_stock
        stockout_detected = current_stock <= 0
        overstock_detected = (
            minimum_stock > 0 and current_stock > minimum_stock * self.OVERSTOCK_MULTIPLIER
        )
        consumption_status = self._compute_consumption_status(daily_consumption)
        priority = self._compute_priority(risk_level, days_remaining)

        return MaterialAnalysis(
            sku=sku,
            name=name,
            category=category,
            unit=unit,
            current_stock=current_stock,
            minimum_stock=minimum_stock,
            daily_consumption=daily_consumption,
            supplier=supplier,
            risk_level=risk_level,
            days_remaining=days_remaining,
            reorder_required=reorder_required,
            stockout_detected=stockout_detected,
            overstock_detected=overstock_detected,
            consumption_status=consumption_status,
            priority=priority,
        )

    def analyze_all(self, rows: list[dict[str, Any]]) -> list[MaterialAnalysis]:
        """Batch analyze all material rows."""
        return [self.analyze_material(row) for row in rows]

    # ── Private helpers ──

    def _compute_risk(self, current: int, minimum: int) -> str:
        if minimum <= 0:
            return "LOW"
        if current <= 0:
            return "HIGH"
        if current < minimum:
            return "HIGH"
        if current <= minimum * self.MEDIUM_RISK_MULTIPLIER:
            return "MEDIUM"
        return "LOW"

    def _compute_days_remaining(self, current: int, consumption: int) -> float | None:
        if consumption <= 0:
            return None
        return round(current / consumption, 1)

    def _compute_consumption_status(self, consumption: int) -> str:
        if consumption <= 0:
            return "ZERO"
        if consumption >= self.HIGH_CONSUMPTION_THRESHOLD:
            return "HIGH"
        if consumption >= self.MEDIUM_CONSUMPTION_THRESHOLD:
            return "MEDIUM"
        return "LOW"

    def _compute_priority(self, risk: str, days_remaining: float | None) -> str:
        if risk == "HIGH" and days_remaining is not None and days_remaining <= 3:
            return "CRITICAL"
        if risk == "HIGH":
            return "HIGH"
        if risk == "MEDIUM":
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _to_int(value: Any) -> int:
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return 0
