from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from .config import settings
from .proxy import forwarder, extract_target_url, ProxyForwarder
from .middleware import AuthenticationMiddleware
from .ratelimit_middleware import RateLimitMiddleware
from .auth import authenticate_request

logger = logging.getLogger(__name__)
# setting logging level to info
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI(
    title="Open Proxy Python",
    description="HTTP/HTTPS proxy server compatible with requests library",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication middleware (if enabled)
if settings.auth_enabled:
    app.add_middleware(AuthenticationMiddleware)

# Rate limiting middleware (if enabled)
if settings.rate_limit_enabled:
    app.add_middleware(RateLimitMiddleware)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "open-proxy-python"}


class ProxyMiddleware(BaseHTTPMiddleware):
    """Middleware to handle X-Target-URL header for proxy requests."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip non-proxy requests (health check, etc.)
        if request.url.path.startswith("/health"):
            return await call_next(request)
        
        # Handle CONNECT separately
        if request.method == "CONNECT":
            logger.info("CONNECT request detected - not supported")
            return await forwarder.handle_connect(request)
        
        # Check if X-Target-URL header is present
        target_url = request.headers.get("X-Target-URL")
        if target_url:
            logger.info("Proxy request with X-Target-URL: %s", target_url)
            if not target_url.startswith(('http://', 'https://')):
                raise HTTPException(
                    status_code=400,
                    detail="Target URL must start with http:// or https://",
                )
            # Check authentication before forwarding
            auth_header = request.headers.get("Proxy-Authorization")
            if not authenticate_request(auth_header):
                logger.warning("Authentication failed for proxy request to %s", target_url)
                return JSONResponse(
                    status_code=407,
                    content={
                        "detail": "Proxy authentication required",
                        "error": "Proxy-Authentication-Required",
                    },
                    headers={
                        "Proxy-Authenticate": f'Basic realm="{settings.auth_realm}"',
                        "Content-Type": "application/json",
                    },
                )
            return await forwarder.forward_request(request, target_url)
        
        # Let the route handler deal with forward proxy requests
        return await call_next(request)


# Add the proxy middleware first
app.add_middleware(ProxyMiddleware)


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "CONNECT"])
async def proxy(request: Request, path: str):
    """Catch-all proxy route for forward proxy requests."""
    logger.info("Proxy request: %s %s", request.method, request.url.path)
    
    # Handle CONNECT separately
    if request.method == "CONNECT":
        logger.info("CONNECT request detected in route handler - not supported")
        return await forwarder.handle_connect(request)
    
    target_url = extract_target_url(request)
    if not target_url:
        # If no target URL provided, return error
        raise HTTPException(
            status_code=400,
            detail="Missing target URL. Provide X-Target-URL header or target_url query parameter.",
        )
    
    # Validate URL scheme
    if not target_url.startswith(('http://', 'https://')):
        raise HTTPException(
            status_code=400,
            detail="Target URL must start with http:// or https://",
        )
    
    return await forwarder.forward_request(request, target_url)


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    logger.info("Starting Open Proxy Python server on %s:%s", settings.proxy_host, settings.proxy_port)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    await forwarder.close()
    logger.info("Shutting down Open Proxy Python server")
