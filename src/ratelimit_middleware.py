"""Rate limiting middleware for FastAPI."""

import logging
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .config import settings
from .auth import get_authenticated_username
from .ratelimit import rate_limiter, RateLimitInfo

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces per-user rate limits on proxy requests."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.rate_limit_enabled = settings.rate_limit_enabled

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health endpoint
        if request.url.path == "/health":
            return await call_next(request)

        # If rate limiting is disabled, proceed
        if not self.rate_limit_enabled:
            return await call_next(request)

        # Get authenticated username
        auth_header = request.headers.get("Proxy-Authorization")
        username = get_authenticated_username(auth_header)

        # If auth is enabled but user is not authenticated, skip rate limiting
        # (auth middleware will handle the 407 response)
        if settings.auth_enabled and username is None:
            return await call_next(request)

        # Get rate limits for user
        per_minute, per_month = 60, 10000  # defaults
        if username is not None:
            from .auth import get_user_manager
            user_manager = get_user_manager()
            per_minute, per_month = user_manager.get_user_rate_limits(username)

        # Check rate limit
        allowed, info = rate_limiter.check_rate_limit(username or "anonymous", per_minute, per_month)

        if not allowed:
            logger.warning(
                "Rate limit exceeded for user %s: minute=%d, month=%d",
                username, per_minute, per_month
            )
            return self._rate_limit_exceeded_response(info)

        # Process request and add rate limit headers
        response = await call_next(request)
        self._add_rate_limit_headers(response, info)

        return response

    def _rate_limit_exceeded_response(self, info: RateLimitInfo) -> Response:
        """Return a 429 Too Many Requests response."""
        headers = {
            "Retry-After": str(info.retry_after or 60),
            "X-RateLimit-Limit-Minute": str(info.limit_per_minute),
            "X-RateLimit-Remaining-Minute": "0",
            "X-RateLimit-Limit-Month": str(info.limit_per_month),
            "X-RateLimit-Remaining-Month": "0",
        }
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded",
                "error": "RateLimit-Exceeded",
                "retry_after": info.retry_after or 60,
            },
            headers=headers,
        )

    def _add_rate_limit_headers(self, response: Response, info: RateLimitInfo) -> None:
        """Add rate limit headers to the response."""
        response.headers["X-RateLimit-Limit-Minute"] = str(info.limit_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(info.remaining_per_minute)
        response.headers["X-RateLimit-Limit-Month"] = str(info.limit_per_month)
        response.headers["X-RateLimit-Remaining-Month"] = str(info.remaining_per_month)
