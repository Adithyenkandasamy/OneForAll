"""ID generation helpers (UUID4 hex strings, DB-friendly)."""

from __future__ import annotations

import uuid


def new_id() -> str:
    return uuid.uuid4().hex
