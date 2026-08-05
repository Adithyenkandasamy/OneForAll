"""Inventory agent HTTP endpoints.

Every route requires authentication. Mutating routes additionally enforce
operator/admin roles inside the service.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.agents.inventory.dependencies import get_inventory_service
from app.agents.inventory.schemas import (
    InventoryAnalysisResponse,
    InventoryQuestion,
    InventorySearchResponse,
    InventoryUpdateRequest,
    InventoryUpdateResponse,
)
from app.agents.inventory.service import InventoryService
from app.api.deps import CurrentUser

router = APIRouter(prefix="/agents/inventory", tags=["agents"])


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
