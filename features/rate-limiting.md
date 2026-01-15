# Rate Limiting Feature

## Overview
Per-user rate limiting to control request frequency and prevent abuse. Each user can have individual rate limits for requests per minute and per month.

## Status
**Completed** - Implemented and tested.

## Configuration

### users.json Format
Each user in `config/users.json` can have the following fields:

```json
{
    "username": {
        "password": "user_password",
        "rate_limit_per_minute": 60,
        "rate_limit_per_month": 10000
    }
}
```

### Fields
| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `password` | string | User's password for authentication | Required |
| `rate_limit_per_minute` | integer | Maximum requests per 60-second window | 60 |
| `rate_limit_per_month` | integer | Maximum requests per 30-day window | 10000 |

### Backward Compatibility
The system supports the old format for backward compatibility:

```json
{
    "username": "password"
}
```

Users with the old format will use default rate limits (60/minute, 10000/month).

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RATE_LIMIT_ENABLED` | Enable/disable rate limiting | `false` |
| `AUTH_ENABLED` | Enable/disable authentication | `false` |

## Response Headers

When rate limiting is enabled, responses include the following headers:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit-Minute` | Maximum requests allowed per minute |
| `X-RateLimit-Remaining-Minute` | Remaining requests in current minute window |
| `X-RateLimit-Limit-Month` | Maximum requests allowed per month |
| `X-RateLimit-Remaining-Month` | Remaining requests in current month window |

## Rate Limit Exceeded Response

When a user exceeds their rate limit, the server returns:

**HTTP Status:** `429 Too Many Requests`

**Response Body:**
```json
{
    "detail": "Rate limit exceeded",
    "error": "RateLimit-Exceeded",
    "retry_after": 30
}
```

**Headers:**
- `Retry-After: 30` - Seconds until the request can be retried
- `X-RateLimit-Limit-Minute: 60`
- `X-RateLimit-Remaining-Minute: 0`
- `X-RateLimit-Limit-Month: 10000`
- `X-RateLimit-Remaining-Month: 0`

## Algorithm

The rate limiter uses a **sliding window** algorithm:

1. **Per-Minute Window**: Tracks requests in a 60-second sliding window
2. **Per-Month Window**: Tracks requests in a 30-day sliding window

For each request:
1. Old requests outside the windows are cleaned up
2. Current request counts are calculated
3. Both limits must be satisfied for the request to proceed
4. If allowed, the request timestamp is recorded

## Implementation Details

### Files
- [`src/ratelimit.py`](src/ratelimit.py) - Rate limiter core logic
- [`src/ratelimit_middleware.py`](src/ratelimit_middleware.py) - FastAPI middleware
- [`src/auth.py`](src/auth.py) - Updated UserManager for rate limits
- [`tests/test_ratelimit.py`](tests/test_ratelimit.py) - Unit tests

### Classes

#### `RateLimiter`
Main rate limiter class with methods:
- `check_rate_limit(username, per_minute, per_month)` - Check and record a request
- `get_rate_limit_info(username, per_minute, per_month)` - Get status without recording

#### `RateLimitInfo`
Dataclass containing:
- `limit_per_minute`: Maximum requests per minute
- `remaining_per_minute`: Remaining requests in current window
- `limit_per_month`: Maximum requests per month
- `remaining_per_month`: Remaining requests in current window
- `retry_after`: Seconds until retry is allowed (only when limited)

#### `RateLimitMiddleware`
FastAPI middleware that:
- Skips rate limiting for `/health` endpoint
- Skips rate limiting if auth is enabled but user not authenticated
- Enforces rate limits and adds headers to responses

## Example Usage

### Configure users.json
```json
{
    "alice": {
        "password": "password123",
        "rate_limit_per_minute": 60,
        "rate_limit_per_month": 10000
    },
    "bob": {
        "password": "secret456",
        "rate_limit_per_minute": 30,
        "rate_limit_per_month": 5000
    }
}
```

### Enable Rate Limiting
```bash
export RATE_LIMIT_ENABLED=true
export AUTH_ENABLED=true
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Client Request with Authentication
```python
import requests

proxies = {
    'http': 'http://localhost:8000',
    'https': 'http://localhost:8000',
}

response = requests.get(
    'https://httpbin.org/get',
    proxies=proxies,
    auth=('alice', 'password123')
)

# Check rate limit headers
print(response.headers.get('X-RateLimit-Remaining-Minute'))
print(response.headers.get('X-RateLimit-Remaining-Month'))
```

## Testing

Run rate limiting tests:
```bash
python -m pytest tests/test_ratelimit.py -v
```

## Limitations

1. **In-Memory Storage**: Rate limit counters are stored in memory and reset on server restart
2. **No Distributed Support**: In multi-worker deployments, each worker has independent counters
3. **Sliding Window Approximation**: Uses simple timestamp-based cleanup, which is efficient but may have minor edge cases with very high request volumes

## Future Enhancements

Potential improvements:
- Redis-backed storage for distributed rate limiting
- Configurable time windows (not just minute/month)
- Rate limit tiers/plans
- Admin endpoint to view rate limit statistics
