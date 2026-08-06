"""Executive Central agent HTTP endpoints.

Every route requires authentication.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser
from app.agents.executive.schemas import ExecutiveQuestion, ExecutiveResponse
from app.agents.executive.service import ExecutiveService

router = APIRouter(prefix="/agents/executive", tags=["agents"])

def get_executive_service() -> ExecutiveService:
    return ExecutiveService()

@router.post("/chat", response_model=ExecutiveResponse)
async def chat(
    payload: ExecutiveQuestion,
    current_user: CurrentUser,
    service: ExecutiveService = Depends(get_executive_service),
) -> dict:
    return await service.answer(
        payload.query,
        user_id=current_user.id,
        role=current_user.role,
        conversation_id=payload.conversation_id,
    )
