"""
Robustness middleware: request body size limit, rate limiting, request ID.
"""
import time
import uuid
from contextvars import ContextVar
from collections import defaultdict
from typing import Callable, List, Optional, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

# In-memory rate limit store: key -> list of timestamps (prune older than 1 min)
_rate_store: dict = defaultdict(list)
# Paths that have stricter rate limits
RATE_LIMIT_PATHS: List[Tuple[str, int]] = [
    ("/api/v1/agent/chat", getattr(settings, "RATE_LIMIT_AGENT_CHAT_PER_MINUTE", 30)),
    ("/api/v1/agent/execute-pending", getattr(settings, "RATE_LIMIT_AGENT_CHAT_PER_MINUTE", 30)),
    ("/api/v1/build/generate", getattr(settings, "RATE_LIMIT_BUILD_GENERATE_PER_MINUTE", 10)),
]


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _get_rate_limit_for_path(path: str) -> Optional[int]:
    for prefix, limit in RATE_LIMIT_PATHS:
        if path == prefix or path.rstrip("/") == prefix.rstrip("/"):
            return limit
    return None


class RequestBodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with body larger than REQUEST_BODY_MAX_BYTES (413)."""

    def __init__(self, app, max_bytes: int | None = None):
        super().__init__(app)
        self.max_bytes = max_bytes or getattr(settings, "REQUEST_BODY_MAX_BYTES", 1_048_576)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": f"Request body too large (max {self.max_bytes} bytes)",
                            "type": "payload_too_large",
                        },
                    )
            except ValueError:
                pass
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP rate limit for expensive endpoints. Returns 429 when exceeded."""

    def __init__(self, app):
        super().__init__(app)
        self.window_sec = 60

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        limit = _get_rate_limit_for_path(path)
        if limit is None:
            return await call_next(request)

        key = _client_ip(request)
        now = time.time()
        # Prune old entries
        self._prune(key, now)
        if len(_rate_store[key]) >= limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded (max {limit} requests per minute)",
                    "type": "rate_limit_exceeded",
                },
            )
        _rate_store[key].append(now)
        return await call_next(request)

    def _prune(self, key: str, now: float) -> None:
        cutoff = now - self.window_sec
        _rate_store[key] = [t for t in _rate_store[key] if t > cutoff]


# ContextVar for request ID (so logging can include it without passing request)
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assign X-Request-ID, set request.state.request_id and request_id_ctx for logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        token = request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)
