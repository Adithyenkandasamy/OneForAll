"""Executive agent DTOs."""

from __future__ import annotations
from pydantic import BaseModel, Field

class ExecutiveQuestion(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None

class ExecutiveResponse(BaseModel):
    content: str
    tool_calls_used: int
    model: str
    risk_flags: list[str] = Field(default_factory=list)
    conversation_id: str | None = None
