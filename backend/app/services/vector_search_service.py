"""Semantic retrieval of meaningful monitoring events through Supabase RPC."""

from __future__ import annotations

from typing import Any

from app.database.supabase import get_supabase_client
from app.services.embedding_service import EmbeddingService, get_embedding_service


class VectorSearchService:
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or get_embedding_service()

    def search_similar_events(self, query: str, limit: int = 5, machine_id: str | None = None,
                              severity: str | None = None) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("Query must not be empty.")
        if not 1 <= limit <= 20:
            raise ValueError("limit must be between 1 and 20.")
        client = get_supabase_client()
        if client is None:
            raise RuntimeError("Supabase is not configured.")
        params: dict[str, Any] = {
            "query_embedding": self.embedding_service.embed_text(query), "match_count": limit,
            "filter_machine_id": machine_id, "filter_severity": severity,
        }
        response = client.rpc("match_monitoring_events", params).execute()
        return response.data or []
