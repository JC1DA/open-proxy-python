import pytest
import httpx
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health endpoint returns OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "open-proxy-python"}


def test_proxy_missing_target():
    """Test proxy endpoint without target URL returns 400."""
    response = client.get("/any/path")
    assert response.status_code == 400
    assert "Missing target URL" in response.json()["detail"]


def test_proxy_invalid_url():
    """Test proxy endpoint with invalid URL returns 400."""
    response = client.get("/any/path", headers={"X-Target-URL": "ftp://example.com"})
    assert response.status_code == 400
    assert "must start with http:// or https://" in response.json()["detail"]


@pytest.mark.asyncio
async def test_proxy_forwarding():
    """Test proxy forwarding to a mock external service."""
    # This test would require a mock server; for now we'll skip
    pass


def test_cors_headers():
    """Test CORS headers are present."""
    response = client.options("/health", headers={"Origin": "http://localhost:3000"})
    assert "access-control-allow-origin" in response.headers
