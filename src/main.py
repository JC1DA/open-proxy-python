from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .config import settings
from .proxy import forwarder, extract_target_url, ProxyForwarder
from .middleware import AuthenticationMiddleware

logger = logging.getLogger(__name__)

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


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "open-proxy-python"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy(request: Request, path: str):
    """Catch-all proxy route."""
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
    logger.info("Starting Open Proxy Python server on %s:%s", settings.host, settings.port)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    await forwarder.close()
    logger.info("Shutting down Open Proxy Python server")
