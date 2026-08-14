"""Natural-language retrieval over historical manufacturing events."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.monitoring import MonitoringSearchRequest, MonitoringSearchResponse
from app.services.vector_search_service import VectorSearchService

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.post("/search", response_model=MonitoringSearchResponse)
def search_monitoring_events(payload: MonitoringSearchRequest) -> MonitoringSearchResponse:
    try:
        results = VectorSearchService().search_similar_events(
            payload.query, payload.limit, payload.machine_id, payload.severity
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return MonitoringSearchResponse(query=payload.query, results=results)
