from fastapi import APIRouter, Query
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


@quality_router.get("/alerts")
async def get_alerts(limit: int = Query(default=20, ge=1, le=100)):
    """Return the latest deterministic monitoring alerts for the alert centre."""
    return await QualityService().get_recent_alerts(limit=limit)


@quality_router.get("/machines/{machine_id}/telemetry")
async def get_machine_telemetry(
    machine_id: str, limit: int = Query(default=20, ge=1, le=200)
):
    """Return only the requested machine's recent telemetry for detail views or AI context."""
    return await QualityService().get_machine_telemetry(machine_id, limit=limit)

@quality_router.post("/chat")
async def quality_chat(req: QualityQueryRequest):
    """Ask natural language queries to the Quality Intelligence AI Explainer."""
    service = QualityService()
    response = await service.answer(req.query)
    return response
