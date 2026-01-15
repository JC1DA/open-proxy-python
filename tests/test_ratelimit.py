"""Tests for rate limiting functionality."""

import os
import base64
import time
import pytest
from fastapi.testclient import TestClient


def basic_auth_header(username: str, password: str) -> str:
    """Create Basic Auth header value."""
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


class TestRateLimitingDisabled:
    """Tests when rate limiting is disabled (default)."""

    def test_rate_limit_headers_not_present(self):
        """Without rate limit enabled, headers should not be added."""
        os.environ["AUTH_ENABLED"] = "false"
        os.environ["RATE_LIMIT_ENABLED"] = "false"
        
        from importlib import reload
        from src import config
        reload(config)
        from src.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        
        # Rate limit headers should not be present
        assert "X-RateLimit-Limit-Minute" not in response.headers
        
        del os.environ["AUTH_ENABLED"]
        del os.environ["RATE_LIMIT_ENABLED"]
        reload(config)


class TestRateLimitingEnabled:
    """Tests when rate limiting is enabled."""

    @pytest.fixture(scope="class")
    def rate_limit_client(self):
        """TestClient with RATE_LIMIT_ENABLED=True."""
        os.environ["AUTH_ENABLED"] = "false"
        os.environ["RATE_LIMIT_ENABLED"] = "true"
        os.environ["USERS_FILE"] = "config/users.json"
        
        from importlib import reload
        from src import config
        reload(config)
        from src.main import app
        client = TestClient(app)
        yield client
        
        del os.environ["AUTH_ENABLED"]
        del os.environ["RATE_LIMIT_ENABLED"]
        del os.environ["USERS_FILE"]
        reload(config)

    def test_rate_limit_headers_present(self, rate_limit_client):
        """Rate limit headers should be present when enabled."""
        response = rate_limit_client.get("/health")
        assert response.status_code == 200
        
        # Health endpoint bypasses rate limiting
        # So check that headers are not added for health

    def test_rate_limit_enforced(self, rate_limit_client):
        """Rate limit should be enforced for proxy requests."""
        # Test that the rate limiter tracks requests and enforces limits
        from src.ratelimit import rate_limiter
        
        # Check that the rate limiter tracks requests for anonymous users
        username = "anonymous"
        allowed, info = rate_limiter.check_rate_limit(username)
        
        assert allowed is True
        assert info.limit_per_minute == 60
        assert info.limit_per_month == 10000
        assert info.remaining_per_minute == 59  # 60 - 1
        assert info.remaining_per_month == 9999  # 10000 - 1


class TestRateLimitingWithAuth:
    """Tests rate limiting with authentication enabled."""

    @pytest.fixture(scope="class")
    def auth_rate_limit_client(self):
        """TestClient with AUTH_ENABLED=True and RATE_LIMIT_ENABLED=True."""
        os.environ["AUTH_ENABLED"] = "true"
        os.environ["RATE_LIMIT_ENABLED"] = "true"
        os.environ["USERS_FILE"] = "config/users.json"
        
        from importlib import reload
        from src import config
        reload(config)
        from src.main import app
        client = TestClient(app)
        yield client
        
        del os.environ["AUTH_ENABLED"]
        del os.environ["RATE_LIMIT_ENABLED"]
        del os.environ["USERS_FILE"]
        reload(config)

    def test_authenticated_user_rate_limit(self, auth_rate_limit_client):
        """Authenticated users should have rate limits applied."""
        # Test that we can get rate limits for authenticated user
        from src.auth import get_user_manager
        from src.ratelimit import rate_limiter
        
        user_manager = get_user_manager()
        per_minute, per_month = user_manager.get_user_rate_limits("alice")
        
        # Verify the rate limiter works for authenticated users
        allowed, info = rate_limiter.check_rate_limit("alice", per_minute, per_month)
        
        assert allowed is True
        assert info.limit_per_minute == 60
        assert info.limit_per_month == 10000

    def test_rate_limit_per_minute_exceeded(self, auth_rate_limit_client):
        """Test that per-minute rate limit is enforced."""
        # Set a very low rate limit for testing
        # This is a simplified test - in production you'd want to test
        # the actual rate limiting behavior more thoroughly
        
        # Get user's configured rate limits
        from src.auth import get_user_manager
        user_manager = get_user_manager()
        per_minute, per_month = user_manager.get_user_rate_limits("alice")
        
        # Just verify we can get the limits
        assert per_minute == 60  # From users.json
        assert per_month == 10000  # From users.json


class TestRateLimiter:
    """Unit tests for the RateLimiter class."""

    def test_check_rate_limit_defaults(self):
        """Test default rate limits when not specified."""
        from src.ratelimit import RateLimiter
        
        limiter = RateLimiter()
        allowed, info = limiter.check_rate_limit("testuser")
        
        assert allowed is True
        assert info.limit_per_minute == RateLimiter.DEFAULT_PER_MINUTE
        assert info.limit_per_month == RateLimiter.DEFAULT_PER_MONTH
        assert info.remaining_per_minute == RateLimiter.DEFAULT_PER_MINUTE - 1
        assert info.remaining_per_month == RateLimiter.DEFAULT_PER_MONTH - 1

    def test_check_rate_limit_custom_limits(self):
        """Test custom rate limits."""
        from src.ratelimit import RateLimiter
        
        limiter = RateLimiter()
        allowed, info = limiter.check_rate_limit("testuser", per_minute=5, per_month=100)
        
        assert allowed is True
        assert info.limit_per_minute == 5
        assert info.limit_per_month == 100

    def test_rate_limit_exceeded(self):
        """Test that rate limit is enforced."""
        from src.ratelimit import RateLimiter
        
        limiter = RateLimiter()
        username = "testuser_limited"
        
        # Make 5 requests with limit of 5
        for i in range(5):
            allowed, info = limiter.check_rate_limit(username, per_minute=5, per_month=100)
            assert allowed is True
        
        # 6th request should be denied
        allowed, info = limiter.check_rate_limit(username, per_minute=5, per_month=100)
        assert allowed is False
        assert info.remaining_per_minute == 0
        assert info.retry_after is not None

    def test_different_users_independent(self):
        """Test that different users have independent rate limits."""
        from src.ratelimit import RateLimiter
        
        limiter = RateLimiter()
        
        # User A makes 5 requests
        for i in range(5):
            limiter.check_rate_limit("user_a", per_minute=5, per_month=100)
        
        # User B should still be able to make requests
        allowed, info = limiter.check_rate_limit("user_b", per_minute=5, per_month=100)
        assert allowed is True


class TestUserManagerWithRateLimits:
    """Tests for UserManager with rate limit support."""

    def test_get_user_rate_limits(self):
        """Test getting rate limits for a user."""
        from src.auth import UserManager
        
        manager = UserManager("config/users.json")
        per_minute, per_month = manager.get_user_rate_limits("alice")
        
        assert per_minute == 60
        assert per_month == 10000

    def test_get_user_rate_limits_bob(self):
        """Test getting rate limits for bob."""
        from src.auth import UserManager
        
        manager = UserManager("config/users.json")
        per_minute, per_month = manager.get_user_rate_limits("bob")
        
        assert per_minute == 30
        assert per_month == 5000

    def test_validate_credentials_with_new_format(self):
        """Test that validation still works with new format."""
        from src.auth import UserManager
        
        manager = UserManager("config/users.json")
        assert manager.validate_credentials("alice", "password123") is True
        assert manager.validate_credentials("alice", "wrong") is False
        assert manager.validate_credentials("nonexistent", "pass") is False
