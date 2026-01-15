"""Tests for proxy server authentication."""

import os
import base64
import pytest
from fastapi.testclient import TestClient

from src.main import app


def basic_auth_header(username: str, password: str) -> str:
    """Create Basic Auth header value."""
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


class TestAuthenticationDisabled:
    """Tests when authentication is disabled (default)."""

    def test_no_auth_required(self):
        """Without auth enabled, requests should succeed."""
        client = TestClient(app)
        # Mock external request will fail because no target URL, but we can test auth
        response = client.get("/any", headers={"X-Target-URL": "http://example.com"})
        # Should get 400 (missing target) not 407
        assert response.status_code == 400
        assert "Missing target URL" in response.json()["detail"]

    def test_auth_header_ignored(self):
        """Auth header is ignored when auth disabled."""
        client = TestClient(app)
        headers = {
            "X-Target-URL": "http://example.com",
            "Proxy-Authorization": basic_auth_header("alice", "password123")
        }
        response = client.get("/any", headers=headers)
        # Still 400 because target not reachable, but not 407
        assert response.status_code == 400


class TestAuthenticationEnabled:
    """Tests when authentication is enabled via environment variable."""

    @pytest.fixture(scope="class")
    def auth_client(self):
        """TestClient with AUTH_ENABLED=True."""
        os.environ["AUTH_ENABLED"] = "true"
        os.environ["USERS_FILE"] = "config/users.json"
        # Need to reload app to pick up new settings
        from importlib import reload
        from src import config
        reload(config)
        from src.main import app
        client = TestClient(app)
        yield client
        del os.environ["AUTH_ENABLED"]
        del os.environ["USERS_FILE"]
        reload(config)

    def test_missing_auth_header(self, auth_client):
        """Request without auth header should return 407."""
        response = auth_client.get("/any", headers={"X-Target-URL": "http://example.com"})
        assert response.status_code == 407
        assert "Proxy-Authenticate" in response.headers
        assert response.headers["Proxy-Authenticate"].startswith("Basic realm=")

    def test_invalid_credentials(self, auth_client):
        """Request with invalid credentials should return 407."""
        headers = {
            "X-Target-URL": "http://example.com",
            "Proxy-Authorization": basic_auth_header("alice", "wrong")
        }
        response = auth_client.get("/any", headers=headers)
        assert response.status_code == 407

    def test_valid_credentials(self, auth_client):
        """Request with valid credentials should pass (though target may fail)."""
        headers = {
            "X-Target-URL": "http://example.com",
            "Proxy-Authorization": basic_auth_header("alice", "password123")
        }
        # The request will fail because target is not reachable (connection error)
        # but that's fine; we just need to verify it's not blocked by auth
        response = auth_client.get("/any", headers=headers)
        # Status could be 502 (connection error) or something else
        assert response.status_code != 407
        assert response.status_code != 401

    def test_health_endpoint_bypass(self, auth_client):
        """Health endpoint should not require authentication."""
        response = auth_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_users_json_loading():
    """Test that users.json is loaded correctly."""
    from src.auth import UserManager
    manager = UserManager("config/users.json")
    assert manager.validate_credentials("alice", "password123") is True
    assert manager.validate_credentials("alice", "wrong") is False
    assert manager.validate_credentials("nonexistent", "pass") is False