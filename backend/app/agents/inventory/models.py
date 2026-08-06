"""Inventory domain entities (in-memory views of sheet rows, never persisted)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class InventoryItem:
    sku: str
    name: str
    quantity: int
    reorder_point: int | None
    unit: str = ""
    status: str = "UNKNOWN"
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> InventoryItem:
        def _int(value: Any, default: int | None = None) -> int | None:
            try:
                return int(float(value))
            except (TypeError, ValueError):
                return default

        qty = _int(row.get("qty") or row.get("quantity") or row.get("stock") or row.get("Current Stock") or 0, 0)
        reorder = _int(row.get("reorder") or row.get("min") or row.get("reorder_point") or row.get("Minimum Stock"))
        status = str(row.get("status") or row.get("AI Risk Level") or row.get("Status") or cls._infer_status(qty, reorder))
        return cls(
            sku=str(row.get("sku") or row.get("SKU") or row.get("Material ID") or row.get("material_id") or ""),
            name=str(row.get("name") or row.get("Name") or row.get("Material") or row.get("material") or ""),
            quantity=qty,
            reorder_point=reorder,
            unit=str(row.get("unit") or ""),
            status=status,
            raw=row,
        )

    @staticmethod
    def _infer_status(quantity: int, reorder: int | None) -> str:
        if reorder is None:
            return "UNKNOWN"
        if quantity <= 0:
            return "STOCKOUT"
        if quantity <= reorder:
            return "LOW"
        return "OK"


@dataclass
class StockSnapshot:
    items: list[InventoryItem] = field(default_factory=list)

    @property
    def low_stock(self) -> list[InventoryItem]:
        return [item for item in self.items if item.status == "LOW"]

    @property
    def stockouts(self) -> list[InventoryItem]:
        return [item for item in self.items if item.status == "STOCKOUT"]
