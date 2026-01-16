# FastAPI HTTP Proxy Server

## Project Overview

A lightweight FastAPI server that acts as an HTTP/HTTPS forwarding proxy, compatible with the `proxies` argument in Python's `requests` library. This allows developers to route requests through a local proxy server for debugging, testing, or network configuration purposes.

## Goals

- Provide a simple, fast proxy server that forwards HTTP/HTTPS requests.
- Support the standard `proxies` dictionary format used by `requests`.
- Minimal dependencies and easy setup.
- Well-documented API and usage examples.

## Target Audience

- Python developers needing a local proxy for testing API clients.
- Developers working with web scraping or network debugging.
- Teams requiring a configurable proxy for development environments.

## Key Features

1. **HTTP/HTTPS Forwarding**: Accepts incoming HTTP/HTTPS requests and forwards them to the target URL.
2. **Requests Library Compatibility**: Can be used as a proxy endpoint in the `proxies` parameter of `requests.get()`/`requests.post()` etc.
3. **CORS Support**: Enable cross-origin requests for browser-based clients.
4. **Basic Logging**: Log request details for debugging.
5. **Health Endpoint**: Simple endpoint to verify server status.
6. **Per-User Rate Limiting**: Configure request limits per user (requests/minute and requests/month).
7. **Basic Authentication**: Optional authentication with configurable user credentials.

## Technology Stack

- **Python 3.11+**
- **FastAPI** for web framework
- **Uvicorn** for ASGI server
- **httpx** or **aiohttp** for asynchronous forwarding (to be decided)
- **Pydantic** for request/response validation (optional)

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- `uv` package manager (recommended) or `pip`

### Installation
1. Clone the repository.
2. Install dependencies: `uv sync`
3. Run the server: `uvicorn src.main:app --reload`

### Usage Example with Requests
```python
import requests

proxies = {
    'http': 'http://localhost:8000',
    'https': 'http://localhost:8000',
}
response = requests.get('https://httpbin.org/get', proxies=proxies)
print(response.json())
```

## Project Structure
```
open-proxy-python/
├── src/
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point
│   ├── proxy.py         # Core proxy logic
│   └── config.py        # Configuration settings
├── tests/
├── pyproject.toml
├── README.md
├── description.md
└── plan.md
```

## Dependencies

- `fastapi>=0.104.0`
- `uvicorn[standard]>=0.24.0`
- `httpx>=0.25.0` (for async HTTP client)
- `python-multipart` (if handling form data)

## Configuration

Configuration can be done via environment variables or a `.env` file. The application uses `pydantic-settings` for configuration management, which automatically loads variables from a `.env` file in the project root.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROXY_HOST` | `0.0.0.0` | Server bind address |
| `PROXY_PORT` | `8000` | Server port |
| `LOG_LEVEL` | `info` | Logging level (debug, info, warning, error, critical) |
| `DEBUG` | `false` | Debug mode toggle (true/false) |
| `ALLOWED_ORIGINS` | `*` | Comma-separated list of allowed CORS origins |
| `FORWARD_TIMEOUT` | `30.0` | Proxy request timeout in seconds |
| `MAX_REDIRECTS` | `10` | Maximum number of redirect hops |
| `VERIFY_SSL` | `true` | Whether to verify SSL certificates (true/false) |
| `AUTH_ENABLED` | `false` | Enable/disable authentication (true/false) |
| `USERS_FILE` | `config/users.json` | Path to users configuration file |
| `AUTH_REALM` | `Open Proxy` | Authentication realm name |
| `RATE_LIMIT_ENABLED` | `false` | Enable/disable rate limiting (true/false) |

### Using .env File

Copy `.env.example` to `.env` and modify the values:

```bash
cp .env.example .env
```

Then edit `.env` with your desired configuration. The `.env` file is automatically ignored by version control.

### Rate Limiting

Rate limiting is configured per-user in `config/users.json`:

```json
{
    "alice": {
        "password": "password123",
        "rate_limit_per_minute": 60,
        "rate_limit_per_month": 10000
    }
}
```

Response headers include:
- `X-RateLimit-Limit-Minute`
- `X-RateLimit-Remaining-Minute`
- `X-RateLimit-Limit-Month`
- `X-RateLimit-Remaining-Month`

Exceeded limits return HTTP 429 with `Retry-After` header.

## Future Enhancements

- Request/response modification hooks
- Metrics and monitoring endpoints
- Docker containerization
- Redis-backed distributed rate limiting
