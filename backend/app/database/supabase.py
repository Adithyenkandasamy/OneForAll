"""Supabase client factory (auth, storage, notifications integration).

Supabase is used for platform-owned data. In this codebase the primary
persistence is SQLAlchemy against the same Postgres; this factory provides
the official Supabase client for auth flows and future realtime features.
"""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_supabase_client() -> Any:
    """Return a configured supabase-py client or None when credentials are absent."""
    if not settings.supabase_url or not settings.supabase_service_role_key:
        logger.info("Supabase credentials not configured; using SQLAlchemy only.")
        return None
    try:
        from supabase import create_client

        return create_client(settings.supabase_rest_url, settings.supabase_service_role_key)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Supabase client init failed", extra={"error": str(exc)})
        return None
