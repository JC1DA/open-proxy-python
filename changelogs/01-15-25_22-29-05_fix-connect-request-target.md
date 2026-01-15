# Fix CONNECT Request Target Handling

## Date
2025-01-15

## Description
Fixed a bug where the proxy server couldn't handle HTTP CONNECT requests for HTTPS tunneling.

## Root Cause
FastAPI doesn't expose the CONNECT request target (host:port) in `request.url.path`. The original code was trying to read from `request.url.path.lstrip("/")` which returned an empty string for CONNECT requests.

## Changes
- Modified `src/proxy.py` to read the CONNECT target from `request.scope['raw_path']` instead of `request.url.path`
- Added URL decoding using `urllib.parse.unquote()` to handle encoded characters (e.g., `%3A` for `:`)

## Files Changed
- `src/proxy.py` - Fixed `handle_connect` method

## Testing
- Verified CONNECT requests are now properly parsed
- Proxy successfully forwards HTTP requests through the server