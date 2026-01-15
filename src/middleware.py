"""Authentication middleware for FastAPI."""

import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .config import settings
from .auth import authenticate_request

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware that validates Basic Authentication for proxy requests."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.auth_enabled = settings.auth_enabled
        self.realm = settings.auth_realm

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip authentication for health endpoint
        if request.url.path == "/health":
            return await call_next(request)
        
        # If authentication is disabled, proceed
        if not self.auth_enabled:
            return await call_next(request)
        
        # Extract Proxy-Authorization header
        auth_header = request.headers.get("Proxy-Authorization")
        
        if not auth_header:
            logger.warning("Missing Proxy-Authorization header")
            return self._unauthorized_response()
        
        # Authenticate
        if not authenticate_request(auth_header):
            logger.warning("Authentication failed for request to %s", request.url.path)
            return self._unauthorized_response()
        
        # Authentication successful
        logger.debug("Authentication passed for %s", request.url.path)
        return await call_next(request)
    
    def _unauthorized_response(self) -> Response:
        """Return a 407 Proxy Authentication Required response."""
        headers = {
            "Proxy-Authenticate": f'Basic realm="{self.realm}"',
            "Content-Type": "application/json",
        }
        return JSONResponse(
            status_code=407,
            content={
                "detail": "Proxy authentication required",
                "error": "Proxy-Authentication-Required",
            },
            headers=headers,
        )