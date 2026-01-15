"""Rate limiting module with sliding window algorithm."""

import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = __import__("logging").getLogger(__name__)


@dataclass
class RateLimitInfo:
    """Rate limit information for a user."""
    limit_per_minute: int
    remaining_per_minute: int
    limit_per_month: int
    remaining_per_month: int
    retry_after: Optional[int] = None


class RateLimiter:
    """Sliding window rate limiter for per-user rate limits."""

    # Time windows in seconds
    MINUTE_WINDOW = 60
    MONTH_WINDOW = 30 * 24 * 60 * 60  # 30 days

    # Default rate limits
    DEFAULT_PER_MINUTE = 60
    DEFAULT_PER_MONTH = 10000

    def __init__(self):
        # Store timestamps for each user: {username: [timestamp1, timestamp2, ...]}
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def _cleanup_old_requests(self, username: str, window_seconds: float) -> None:
        """Remove requests outside the sliding window."""
        cutoff = time.time() - window_seconds
        self.requests[username] = [
            ts for ts in self.requests[username] if ts > cutoff
        ]

    def _count_requests_in_window(self, username: str, window_seconds: float) -> int:
        """Count requests within a time window."""
        cutoff = time.time() - window_seconds
        return sum(1 for ts in self.requests[username] if ts > cutoff)

    def check_rate_limit(
        self,
        username: str,
        per_minute: Optional[int] = None,
        per_month: Optional[int] = None,
    ) -> Tuple[bool, RateLimitInfo]:
        """Check if a request is allowed based on rate limits.

        Args:
            username: The username making the request
            per_minute: Maximum requests per minute (default: 60)
            per_month: Maximum requests per month (default: 10000)

        Returns:
            Tuple of (allowed: bool, rate_limit_info: RateLimitInfo)
        """
        # Use defaults if not specified
        if per_minute is None:
            per_minute = self.DEFAULT_PER_MINUTE
        if per_month is None:
            per_month = self.DEFAULT_PER_MONTH

        # Cleanup old requests
        self._cleanup_old_requests(username, self.MINUTE_WINDOW)
        self._cleanup_old_requests(username, self.MONTH_WINDOW)

        # Count current requests in each window
        current_minute = self._count_requests_in_window(username, self.MINUTE_WINDOW)
        current_month = self._count_requests_in_window(username, self.MONTH_WINDOW)

        # Check both limits
        minute_allowed = current_minute < per_minute
        month_allowed = current_month < per_month

        allowed = minute_allowed and month_allowed

        # Calculate remaining (subtract 1 for this request if allowed)
        remaining_minute = max(0, per_minute - current_minute - 1) if allowed else 0
        remaining_month = max(0, per_month - current_month - 1) if allowed else 0

        # Calculate retry after
        retry_after: Optional[int] = None
        if not allowed:
            if not minute_allowed:
                # Find the oldest request in the minute window
                oldest = min(self.requests[username][-per_minute:]) if len(self.requests[username]) >= per_minute else 0
                retry_after = max(1, int(self.MINUTE_WINDOW - (time.time() - oldest)))
            else:
                # Month limit exceeded
                oldest = min(self.requests[username][-per_month:]) if len(self.requests[username]) >= per_month else 0
                retry_after = max(1, int(self.MONTH_WINDOW - (time.time() - oldest)))

        # Record this request if allowed
        if allowed:
            self.requests[username].append(time.time())

        info = RateLimitInfo(
            limit_per_minute=per_minute,
            remaining_per_minute=remaining_minute,
            limit_per_month=per_month,
            remaining_per_month=remaining_month,
            retry_after=retry_after,
        )

        logger.debug(
            "Rate limit check for %s: allowed=%s, minute=%d/%d, month=%d/%d",
            username, allowed, current_minute, per_minute, current_month, per_month
        )

        return allowed, info

    def get_rate_limit_info(
        self,
        username: str,
        per_minute: Optional[int] = None,
        per_month: Optional[int] = None,
    ) -> RateLimitInfo:
        """Get current rate limit status without recording a request."""
        if per_minute is None:
            per_minute = self.DEFAULT_PER_MINUTE
        if per_month is None:
            per_month = self.DEFAULT_PER_MONTH

        # Cleanup old requests
        self._cleanup_old_requests(username, self.MINUTE_WINDOW)
        self._cleanup_old_requests(username, self.MONTH_WINDOW)

        # Count current requests
        current_minute = self._count_requests_in_window(username, self.MINUTE_WINDOW)
        current_month = self._count_requests_in_window(username, self.MONTH_WINDOW)

        return RateLimitInfo(
            limit_per_minute=per_minute,
            remaining_per_minute=max(0, per_minute - current_minute),
            limit_per_month=per_month,
            remaining_per_month=max(0, per_month - current_month),
        )


# Global rate limiter instance
rate_limiter = RateLimiter()
