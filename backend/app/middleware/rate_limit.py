"""Simple in-memory sliding-window rate limiter.

Good enough for a single-process deployment; replace with Redis for the
multi-replica architecture.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.exceptions import ErrorCode

_WINDOW_SECONDS = 60
_MAX_REQUESTS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: object, *, max_requests: int = _MAX_REQUESTS) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self._max_requests = max_requests
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = self._hits[client]
        while window and window[0] <= now - _WINDOW_SECONDS:
            window.popleft()
        if len(window) >= self._max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "code": ErrorCode.RATE_LIMITED.value,
                    "message": "Too many requests",
                    "detail": f"Limit is {self._max_requests} requests per {_WINDOW_SECONDS}s",
                },
            )
        window.append(now)
        return await call_next(request)
