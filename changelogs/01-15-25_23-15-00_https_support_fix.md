# HTTPS Support Fix

**Date:** 2025-01-15

## Description
Fixed HTTPS proxying support by clarifying the correct usage pattern and removing non-functional CONNECT tunneling implementation.

## Root Cause
The proxy server was attempting to support HTTPS through the HTTP CONNECT method, but FastAPI/uvicorn does not support protocol upgrades required for CONNECT tunneling. When clients used the `proxies` parameter with `requests`, it triggered CONNECT tunneling which failed with:
```
h11._util.LocalProtocolError: can't handle event type Data when role=SERVER and state=SWITCHED_PROTOCOL
```

## Changes Made

### Code Changes
1. **src/proxy.py**
   - Simplified [`handle_connect()`](src/proxy.py:126) to return a clear 501 error with usage instructions
   - Removed complex CONNECT target parsing logic that was never functional
   - Added documentation explaining that CONNECT is not supported

2. **src/main.py**
   - Cleaned up debug logging in [`ProxyMiddleware`](src/main.py:46)
   - Cleaned up debug logging in [`proxy()`](src/main.py:78) route handler

3. **tmp/test.py**
   - Updated to use correct HTTPS proxying pattern with `X-Target-URL` header
   - Removed `proxies` parameter which triggered CONNECT tunneling

### Documentation Changes
1. **README.md**
   - Updated usage examples to show correct HTTP and HTTPS request patterns
   - Added note that CONNECT method is not supported
   - Clarified that HTTPS requests should use `X-Target-URL` header

## Testing
- Tested HTTPS request to `https://google.com` successfully
- Verified proxy correctly forwards HTTPS requests using httpx
- Confirmed CONNECT requests now return clear 501 error with usage instructions

## Usage Pattern

### Correct HTTPS Usage
```python
import requests

response = requests.get(
    'http://localhost:8000',
    headers={'X-Target-URL': 'https://example.com'}
)
```

### Incorrect HTTPS Usage (will fail)
```python
import requests

proxies = {
    'https': 'http://localhost:8000',
}
response = requests.get('https://example.com', proxies=proxies)  # ❌ CONNECT not supported
```

## Files Changed
- src/proxy.py
- src/main.py
- tmp/test.py
- README.md
