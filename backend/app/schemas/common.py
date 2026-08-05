"""Common Pydantic DTOs shared across API routes."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ApiMessage(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    detail: str | None = None


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
