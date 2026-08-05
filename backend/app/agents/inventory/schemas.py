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
