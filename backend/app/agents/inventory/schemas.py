"""Inventory agent DTOs (request/response contracts)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class InventoryItemDTO(BaseModel):
    sku: str
    name: str
    quantity: int
    reorder_point: int | None
    unit: str
    status: str


class InventoryQuestion(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None


class InventoryAnalysisResponse(BaseModel):
    content: str
    tool_calls_used: int
    model: str
    risk_flags: list[str] = Field(default_factory=list)
    conversation_id: str | None = None


class InventorySearchResponse(BaseModel):
    items: list[InventoryItemDTO]


class InventoryUpdateRequest(BaseModel):
    sku: str = Field(min_length=1)
    column: str = Field(min_length=1, max_length=64)
    value: str = Field(min_length=1, max_length=128)


class InventoryUpdateResponse(BaseModel):
    message: str
    sku: str
    column: str
    value: str


# ── Enriched DTOs (Phase 2 — deterministic engine outputs) ──


class MaterialAnalysisDTO(BaseModel):
    sku: str
    name: str
    category: str
    unit: str
    current_stock: int
    minimum_stock: int
    daily_consumption: int
    supplier: str
    risk_level: str
    days_remaining: float | None
    reorder_required: bool
    stockout_detected: bool
    overstock_detected: bool
    consumption_status: str
    priority: str


class InventoryHealthDTO(BaseModel):
    total_materials: int
    safe_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    overstock_count: int
    stockout_count: int
    critical_count: int
    reorder_count: int
    health_score: float
    risk_distribution: dict[str, int]


class AnalyticsDTO(BaseModel):
    fast_moving: list[dict]
    slow_moving: list[dict]
    dead_stock: list[dict]
    supplier_stats: dict[str, int]
    top_critical: list[dict]
    abc_analysis: dict[str, list[dict]]
    consumption_summary: dict[str, int]


class DashboardDTO(BaseModel):
    health: InventoryHealthDTO
    top_critical: list[MaterialAnalysisDTO]
    risk_distribution: dict[str, int]
    supplier_stats: dict[str, int]


class ReportDTO(BaseModel):
    report_type: str
    generated_at: str
    health: dict
    total_materials: int
    high_risk_materials: list[dict]
    reorder_list: list[dict]
    stockout_list: list[dict]
    overstock_list: list[dict]
