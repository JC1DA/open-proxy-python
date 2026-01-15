# Authentication Test Plan

## Test Cases

### 1. Authentication Disabled (Default)
- Request without credentials should succeed
- Request with credentials should also succeed (ignored)

### 2. Authentication Enabled
- Request without credentials -> 407 Proxy Authentication Required
- Request with invalid credentials -> 407
- Request with valid credentials -> forward successfully
- Health endpoint should bypass authentication

### 3. Integration with Requests Library
- Test using `proxies = {"http": "http://user:pass@localhost:8000"}`
- Verify requests library adds Proxy-Authorization header
- Verify server accepts it

## Implementation Notes
- Use environment variable `AUTH_ENABLED=true` to enable
- Mock users.json file for tests
- Use base64 encoding for Basic auth header

## Test File Structure
Create `tests/test_auth.py` with:
- Fixtures for TestClient with different configs
- Mock users.json
- Test functions for each scenario