"""Inventory agent exception hierarchy."""

from __future__ import annotations

from app.core.exceptions import AppError, ErrorCode, ForbiddenError, McpUnavailableError


class InventoryAgentError(AppError):
    """Base error for the inventory agent."""

    error_code = ErrorCode.AI_AGENT_ERROR


class SheetUnavailableError(McpUnavailableError):
    """Google Sheets MCP server could not be reached."""


class UnauthorizedToolError(ForbiddenError):
    """User lacks the role required to mutate inventory."""


class InvalidUpdateError(InventoryAgentError):
    """Update request failed validation (e.g. unknown column)."""

    status_code = 422
    error_code = ErrorCode.VALIDATION_ERROR
