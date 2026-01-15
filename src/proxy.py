"""Core proxy forwarding logic."""

import logging
from typing import Optional

import httpx
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

from .config import settings

logger = logging.getLogger(__name__)


class ProxyForwarder:
    """Handles forwarding of HTTP requests."""

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=settings.forward_timeout,
            follow_redirects=True,
            max_redirects=settings.max_redirects,
            verify=settings.verify_ssl,
        )

    async def forward_request(
        self, request: Request, target_url: str
    ) -> Response:
        """Forward the incoming request to the target URL."""
        logger.info(
            "Forwarding %s %s -> %s",
            request.method,
            request.url.path,
            target_url,
        )

        # Prepare request data
        headers = dict(request.headers)
        # Remove hop-by-hop headers
        for h in [
            "host",
            "content-length",
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",  # Remove proxy authorization before forwarding
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
        ]:
            headers.pop(h, None)

        # Read request body
        body = await request.body()

        try:
            # Forward request
            resp = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body if body else None,
                params=dict(request.query_params),
            )
        except httpx.ConnectError as e:
            logger.error("Connection error: %s", e)
            raise HTTPException(
                status_code=502,
                detail=f"Cannot connect to target: {e}",
            )
        except httpx.TimeoutException as e:
            logger.error("Timeout error: %s", e)
            raise HTTPException(
                status_code=504,
                detail="Target request timeout",
            )
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            raise HTTPException(
                status_code=500,
                detail=f"Proxy error: {e}",
            )

        # Build response
        response_headers = dict(resp.headers)
        # Remove hop-by-hop headers from response
        for h in [
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
        ]:
            response_headers.pop(h, None)

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=response_headers,
            media_type=resp.headers.get("content-type"),
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


forwarder = ProxyForwarder()


def extract_target_url(request: Request) -> Optional[str]:
    """Extract target URL from request headers or query parameters."""
    # Check X-Target-URL header
    target_url = request.headers.get("X-Target-URL")
    if target_url:
        return target_url

    # Check query parameter
    target_url = request.query_params.get("target_url")
    if target_url:
        return target_url

    # For compatibility with requests library proxy mode,
    # the target is the original request URL path.
    # In standard proxy usage, the request line contains the full URL.
    # FastAPI doesn't expose that directly, so we rely on the client
    # to provide the target via header.
    return None