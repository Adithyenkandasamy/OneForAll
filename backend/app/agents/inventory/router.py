"""Inventory agent HTTP endpoints.

Every route requires authentication. Mutating routes additionally enforce
operator/admin roles inside the service.

New endpoints (Phase 3):
  GET  /health     — deterministic health snapshot
  GET  /analytics  — structured analytics
  GET  /dashboard  — combined dashboard summary
  POST /report     — generate inventory report
  GET  /materials  — enriched materials with rule engine analysis
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.agents.inventory.dependencies import get_inventory_service
from app.agents.inventory.schemas import (
    AnalyticsDTO,
    DashboardDTO,
    InventoryAnalysisResponse,
    InventoryHealthDTO,
    InventoryQuestion,
    InventorySearchResponse,
    InventoryUpdateRequest,
    InventoryUpdateResponse,
    MaterialAnalysisDTO,
    ReportDTO,
)
from app.agents.inventory.service import InventoryService
from app.api.deps import CurrentUser

router = APIRouter(prefix="/agents/inventory", tags=["agents"])


# ── Existing endpoints (unchanged contracts) ──


@router.post("/chat", response_model=InventoryAnalysisResponse)
async def chat(
    payload: InventoryQuestion,
    current_user: CurrentUser,
    service: InventoryService = Depends(get_inventory_service),
) -> dict:
    return await service.answer(
        payload.query,
        user_id=current_user.id,
        role=current_user.role,
        conversation_id=payload.conversation_id,
    )


@router.get("/search", response_model=InventorySearchResponse)
async def search(
    _: CurrentUser,
    q: str = Query(min_length=1, max_length=500),
    limit: int = Query(default=25, ge=1, le=100),
    service: InventoryService = Depends(get_inventory_service),
) -> dict:
    items = await service.search(q, limit=limit)
    return {"items": items}


@router.post("/update", response_model=InventoryUpdateResponse)
async def update(
    payload: InventoryUpdateRequest,
    current_user: CurrentUser,
    service: InventoryService = Depends(get_inventory_service),
) -> dict:
    return await service.update(
        sku=payload.sku,
        column=payload.column,
        value=payload.value,
        role=current_user.role,
    )


# ── New endpoints (deterministic engines) ──


@router.get("/health", response_model=InventoryHealthDTO)
async def health(
    _: CurrentUser,
    service: InventoryService = Depends(get_inventory_service),
) -> dict:
    return await service.get_health()


@router.get("/analytics", response_model=AnalyticsDTO)
async def analytics(
    _: CurrentUser,
    service: InventoryService = Depends(get_inventory_service),
) -> dict:
    return await service.get_analytics()


@router.get("/dashboard", response_model=DashboardDTO)
async def dashboard(
    _: CurrentUser,
    service: InventoryService = Depends(get_inventory_service),
) -> dict:
    return await service.get_dashboard()


@router.post("/report", response_model=ReportDTO)
async def report(
    _: CurrentUser,
    service: InventoryService = Depends(get_inventory_service),
) -> dict:
    return await service.generate_report()


@router.get("/materials", response_model=list[MaterialAnalysisDTO])
async def enriched_materials(
    _: CurrentUser,
    service: InventoryService = Depends(get_inventory_service),
) -> list[dict]:
    return await service.get_enriched_materials()

