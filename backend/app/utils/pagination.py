"""Pagination helper shared by list endpoints."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Page:
    limit: int
    offset: int

    @classmethod
    def from_params(cls, limit: int | None, offset: int | None, *, max_limit: int = 100) -> Page:
        return cls(limit=min(max(limit or 20, 1), max_limit), offset=max(offset or 0, 0))
