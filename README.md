# Open Proxy Python

A FastAPI HTTP/HTTPS proxy server compatible with Python's `requests` library `proxies` argument.

## Features

- HTTP/HTTPS forwarding with support for all HTTP methods
- Compatible with `requests` library `proxies` parameter
- CORS enabled for browser clients
- Configurable via environment variables
- Health endpoint for monitoring
- Async forwarding using `httpx`

## Installation

1. Install [uv](https://github.com/astral-sh/uv) if not already installed:
   ```bash
   pip install uv
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

## Quick Start

Start the proxy server:

```bash
uvicorn src.main:app --reload
```

The server will run on `http://localhost:8000`.

### Usage with Requests Library

```python
import requests

proxies = {
    'http': 'http://localhost:8000',
    'https': 'http://localhost:8000',
}

# Make a request through the proxy
response = requests.get(
    'https://httpbin.org/get',
    proxies=proxies,
    headers={'X-Target-URL': 'https://httpbin.org/get'}
)
print(response.json())
```

### Direct API Usage

You can also use the proxy directly via HTTP:

```bash
curl -X GET \
  -H "X-Target-URL: https://httpbin.org/get" \
  http://localhost:8000/proxy
```

## Configuration

Environment variables:

- `PROXY_HOST` - Bind host (default: `0.0.0.0`)
- `PROXY_PORT` - Bind port (default: `8000`)
- `LOG_LEVEL` - Logging level (default: `info`)
- `ALLOWED_ORIGINS` - CORS origins (default: `*`)
- `FORWARD_TIMEOUT` - Timeout in seconds (default: `30.0`)
- `VERIFY_SSL` - Verify SSL certificates (default: `true`)

## API Endpoints

- `GET /health` - Health check
- `ANY /{path}` - Proxy endpoint (requires `X-Target-URL` header or `target_url` query parameter)

## Development Setup

This project uses [Ruff](https://docs.astral.sh/ruff/) for code formatting and linting.

### Configuration

- **Line length**: 120 characters
- **Indentation**: 4 spaces
- **Quote style**: Double quotes
- **Target Python version**: 3.11+

### Auto-formatting on Save

VSCode is configured to automatically format Python files on save using Ruff. The configuration is in `.vscode/settings.json`.

### Installation

1. Install [uv](https://github.com/astral-sh/uv) if not already installed:
   ```bash
   pip install uv
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Ruff is installed as a dev dependency.

### Usage

- Format all files:
  ```bash
  ruff format .
  ```

- Lint all files:
  ```bash
  ruff check .
  ```

- Fix lint issues:
  ```bash
  ruff check --fix .
  ```

### Configuration Files

- `ruff.toml`: Ruff configuration with line-length = 120 and other settings.
- `pyproject.toml`: Project metadata and dev dependencies.
- `.vscode/settings.json`: VSCode settings for format on save.

### Notes

- The Ruff formatter will automatically wrap lines longer than 120 characters.
- Unused imports and variables are ignored (F401, F841) for convenience.
- Missing docstrings are ignored (D) for now.
