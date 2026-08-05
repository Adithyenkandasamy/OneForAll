"""Application exception hierarchy.

Every domain/service exception derives from ``AppError`` so the single
error handler in ``app/middleware/error_handler.py`` can map it to an
HTTP response with a stable error code. Agents define their own
``AgentError`` subclasses which bubble up to the service boundary and are
mapped here.
"""

from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    AI_AGENT_ERROR = "AI_AGENT_ERROR"
    MCP_UNAVAILABLE = "MCP_UNAVAILABLE"
    LLM_UNAVAILABLE = "LLM_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AppError(Exception):
    """Base class for all expected application errors."""

    status_code = 500
    error_code = ErrorCode.INTERNAL_ERROR

    def __init__(self, message: str, *, detail: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail

    def to_dict(self) -> dict[str, str | None]:
        return {
            "code": self.error_code.value,
            "message": self.message,
            "detail": self.detail,
        }


class BadRequestError(AppError):
    status_code = 400
    error_code = ErrorCode.BAD_REQUEST


class ValidationAppError(AppError):
    status_code = 422
    error_code = ErrorCode.VALIDATION_ERROR


class UnauthorizedError(AppError):
    status_code = 401
    error_code = ErrorCode.UNAUTHORIZED


class ForbiddenError(AppError):
    status_code = 403
    error_code = ErrorCode.FORBIDDEN


class NotFoundError(AppError):
    status_code = 404
    error_code = ErrorCode.NOT_FOUND


class ConflictError(AppError):
    status_code = 409
    error_code = ErrorCode.CONFLICT


class RateLimitedError(AppError):
    status_code = 429
    error_code = ErrorCode.RATE_LIMITED


class McpUnavailableError(AppError):
    status_code = 503
    error_code = ErrorCode.MCP_UNAVAILABLE


class LlmUnavailableError(AppError):
    status_code = 503
    error_code = ErrorCode.LLM_UNAVAILABLE
