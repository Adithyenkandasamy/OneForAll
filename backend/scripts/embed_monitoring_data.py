"""Ingest meaningful mock monitoring events into Supabase pgvector.

Run from ``backend``: ``python scripts/embed_monitoring_data.py``.
The migration in ``migrations/20260814_monitoring_embeddings.sql`` must run first.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.database.supabase import get_supabase_client  # noqa: E402
from app.services.embedding_service import EMBEDDING_DIMENSION, get_embedding_service  # noqa: E402
from app.services.monitoring_event_text import (  # noqa: E402
    monitoring_event_to_text,
    validate_monitoring_event,
)

DATA_FILE = BACKEND_DIR / "data" / "monitoring_events.json"


def metadata_for(event: dict[str, Any]) -> dict[str, Any]:
    excluded = {"event_id", "machine_id", "event_type", "severity"}
    return {key: value for key, value in event.items() if key not in excluded}


def main() -> None:
    client = get_supabase_client()
    if client is None:
        raise SystemExit("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in backend/.env.")
    events = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if not isinstance(events, list):
        raise SystemExit("monitoring_events.json must contain a JSON array.")
    print("Loading embedding model...")
    embedding_service = get_embedding_service()
    print(f"Loaded {len(events)} events.\nGenerating embeddings...")
    inserted = skipped = failed = 0
    seen: set[str] = set()
    for event in events:
        try:
            validate_monitoring_event(event)
            event_id = event["event_id"]
            if event_id in seen:
                raise ValueError(f"Duplicate event_id in JSON: {event_id}")
            seen.add(event_id)
            existing = (
                client.table("monitoring_embeddings")
                .select("event_id")
                .eq("event_id", event_id)
                .limit(1)
                .execute()
            )
            if existing.data:
                skipped += 1
                continue
            content = monitoring_event_to_text(event)
            row = {
                "event_id": event_id,
                "machine_id": event["machine_id"],
                "event_type": event["event_type"],
                "severity": event["severity"],
                "content": content,
                "metadata": metadata_for(event),
                "embedding": embedding_service.embed_text(content),
            }
            client.table("monitoring_embeddings").insert(row).execute()
            inserted += 1
        except Exception as exc:  # keeps batch ingestion resilient
            failed += 1
            print(f"Failed {event.get('event_id', '<unknown>')}: {exc}")
    print(
        f"\nInserted: {inserted}\nSkipped: {skipped}\nFailed: {failed}"
        f"\nEmbedding dimension: {EMBEDDING_DIMENSION}"
    )


if __name__ == "__main__":
    main()
