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

Configuration can be done via environment variables:
- `PROXY_HOST`: Bind host (default: `0.0.0.0`)
- `PROXY_PORT`: Bind port (default: `8000`)
- `LOG_LEVEL`: Logging level (default: `info`)
- `ALLOWED_ORIGINS`: CORS origins (default: `*`)

## Future Enhancements

- Authentication support (API key, basic auth)
- Rate limiting
- Request/response modification hooks
- Metrics and monitoring endpoints
- Docker containerization
