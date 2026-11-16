"""
In-memory sliding-window rate limiting.

Intended as a single-process safeguard; deployments behind multiple workers
should use a shared store (e.g. Redis) instead.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float | None = None) -> bool:
        current = time.monotonic() if now is None else now
        hits = self._hits[key]
        cutoff = current - self.window_seconds

        while hits and hits[0] <= cutoff:
            hits.popleft()

        if len(hits) >= self.max_requests:
            return False

        hits.append(current)
        return True

    def reset(self) -> None:
        self._hits.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        max_requests: int = 120,
        window_seconds: float = 60,
        exempt_paths: tuple[str, ...] = (
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/health",
        ),
    ) -> None:
        super().__init__(app)
        self.limiter = SlidingWindowLimiter(max_requests, window_seconds)
        self.exempt_paths = exempt_paths

    def _is_exempt(self, path: str) -> bool:
        return any(
            path == exempt or path.startswith(exempt + "/")
            for exempt in self.exempt_paths
        )

    async def dispatch(self, request: Request, call_next):
        if self._is_exempt(request.url.path):
            return await call_next(request)

        client_key = request.client.host if request.client else "anonymous"
        if not self.limiter.allow(client_key):
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "detail": "Rate limit exceeded. Please retry shortly.",
                },
            )

        return await call_next(request)
