from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.quality.services.service import QualityService

quality_router = APIRouter(tags=["Quality AI"])

class QualityQueryRequest(BaseModel):
    query: str

@quality_router.get("/dashboard")
async def get_dashboard():
    """Retrieve realtime sensor states and calculated metrics for the frontend Dashboard."""
    service = QualityService()
    data = await service.get_dashboard_state()
    return data

@quality_router.post("/chat")
async def quality_chat(req: QualityQueryRequest):
    """Ask natural language queries to the Quality Intelligence AI Explainer."""
    service = QualityService()
    response = await service.answer(req.query)
    return response

