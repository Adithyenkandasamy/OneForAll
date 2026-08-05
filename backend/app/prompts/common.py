"""Shared prompt fragments used across agents."""

from __future__ import annotations

COMMON_GUARDRAILS = (
    "Never invent data. If information is missing, say so. "
    "Ground every claim in the tool results you received."
)

ANSWER_FORMAT = (
    "Answer concisely. Prefer short bullet lists or a small table when comparing multiple items."
)
