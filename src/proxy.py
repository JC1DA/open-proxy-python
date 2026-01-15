"""Core proxy forwarding logic."""

import asyncio
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
        
        # Ensure Accept-Encoding is present so httpx can handle gzip properly
        if "accept-encoding" not in headers:
            headers["accept-encoding"] = "gzip, deflate, br"

        # Read request body
        body = await request.body()

        try:
            # Forward request
            resp = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body if body else None,
                params=dict(request.query_params)
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

        # Debug: Log content-encoding header
        if "content-encoding" in resp.headers:
            logger.debug("Original content-encoding: %s", resp.headers.get("content-encoding"))
            logger.debug("Content length in response: %d bytes", len(resp.content))
        
        # httpx automatically decompresses content when Accept-Encoding is set.
        # The content-encoding header is still present in resp.headers, but resp.content
        # contains DECOMPRESSED data. We must remove content-encoding to prevent the
        # client from trying to decompress already-decompressed content.
        if "content-encoding" in response_headers:
            logger.debug("Removing content-encoding header to avoid double-decompression")
            response_headers.pop("content-encoding", None)
            response_headers.pop("content-length", None)
        
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=response_headers,
            media_type=resp.headers.get("content-type"),
        )

    async def handle_connect(self, request: Request) -> Response:
        """Handle HTTP CONNECT tunneling for HTTPS proxying."""
        # Extract host:port from CONNECT request target
        # For CONNECT requests, the target is in request.scope['raw_path'] or request.url.path
        # The raw_path contains the URL-encoded target like "google.com%3A443"
        import urllib.parse
        
        # Try raw_path first (contains encoded target)
        raw_path = request.scope.get('raw_path', b'').decode('utf-8')
        if not raw_path:
            # Fallback to url.path
            raw_path = request.url.path.lstrip("/")
        
        target = urllib.parse.unquote(raw_path)
        
        if not target:
            raise HTTPException(
                status_code=400,
                detail="CONNECT request must specify host:port",
            )
        
        # URL decode the target (colon may be encoded as %3A)
        import urllib.parse
        target = urllib.parse.unquote(target)
        
        # Parse host and port
        if ":" not in target:
            host = target
            port = 443
        else:
            host, port_str = target.split(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid port in CONNECT target: {port_str}",
                )
        
        logger.info("CONNECT tunneling to %s:%s", host, port)
        
        # For now, we just return 200 to let the client think tunneling is established.
        # Actual tunneling is not implemented because FastAPI does not support raw socket upgrade.
        # This will allow HTTPS proxying but the tunnel will be broken after 200.
        # In production, you'd need to use an ASGI server that supports raw socket upgrade.
        return Response(
            content=None,
            status_code=200,
            headers={
                "Connection": "keep-alive",
                "Proxy-Agent": "Open Proxy Python",
            },
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


forwarder = ProxyForwarder()


def extract_target_url(request: Request) -> Optional[str]:
    """Extract target URL from request headers, query parameters, or request line."""
    # Check X-Target-URL header
    target_url = request.headers.get("X-Target-URL")
    if target_url:
        return target_url

    # Check query parameter
    target_url = request.query_params.get("target_url")
    if target_url:
        return target_url

    # For forward proxy mode, the request line contains the full URL.
    # FastAPI's request.url.path includes the full URL (encoded).
    # Decode and check if it looks like a URL.
    import urllib.parse
    path = request.url.path.lstrip("/")
    if path:
        decoded = urllib.parse.unquote(path)
        if decoded.startswith(("http://", "https://")):
            return decoded
    
    return None