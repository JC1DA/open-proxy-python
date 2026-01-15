# Basic Authentication Implementation Plan

## Overview
Add support for HTTP Basic Authentication to the proxy server, allowing clients to authenticate using credentials in the proxy URL (e.g., `http://username:password@localhost:8000`). Credentials are validated against a `users.json` file.

## Requirements
1. Support proxy URLs with embedded credentials: `http://username:password@localhost:8000`
2. Load user credentials from `config/users.json` file at startup
3. Validate incoming requests that include `Proxy-Authorization` header (Basic Auth)
4. Reject unauthorized requests with HTTP 407 Proxy Authentication Required
5. Maintain backward compatibility: if authentication is not configured, allow unauthenticated requests

## Design

### Authentication Flow
```mermaid
graph TD
    A[Client Request with Proxy URL] --> B{Proxy URL contains credentials?}
    B -->|Yes| C[Requests library adds Proxy-Authorization header]
    B -->|No| D[No authentication]
    C --> E[FastAPI middleware extracts header]
    E --> F{Validate against users.json}
    F -->|Valid| G[Forward request]
    F -->|Invalid| H[Return 407 with Proxy-Authenticate header]
    D --> I[Check if auth required]
    I -->|Auth optional| G
    I -->|Auth required| H
```

### File Structure
- `config/users.json`: JSON object mapping usernames to passwords (plaintext for now)
- `src/auth.py`: Authentication module with credential loading and validation
- `src/middleware.py`: FastAPI middleware for authentication
- Update `src/config.py` to add authentication settings
- Update `src/main.py` to include middleware

### Configuration
Add to `Settings` class:
- `auth_enabled: bool = False`
- `users_file: str = "config/users.json"`
- `auth_realm: str = "Open Proxy"`

### Middleware Design
1. Intercept all requests before reaching proxy route
2. Skip authentication for `/health` endpoint
3. Parse `Proxy-Authorization` header (Basic scheme)
4. Validate credentials against loaded users
5. If invalid or missing, return `407 Proxy Authentication Required` with `Proxy-Authenticate: Basic realm="Open Proxy"`

### Credential Loading
- Load JSON file at startup
- Cache in memory
- Reload on file change (optional)
- Format: `{"username1": "password1", "username2": "password2"}`

### Compatibility with Requests Library
When using `proxies = {"http": "http://user:pass@localhost:8000"}`, the requests library automatically adds a `Proxy-Authorization` header with Basic auth. Our server must recognize this header.

## Implementation Steps

1. **Create config/users.json** with example credentials
2. **Extend Settings class** in config.py
3. **Create auth.py** with UserManager class
4. **Create middleware.py** with authentication middleware
5. **Update main.py** to add middleware conditionally
6. **Update proxy.py** to pass authentication context (optional)
7. **Write unit tests** for authentication
8. **Update documentation** and README

## Testing Strategy
- Test valid credentials succeed
- Test invalid credentials return 407
- Test missing credentials when auth enabled
- Test disabled auth allows all requests
- Test with actual requests library proxy URL

## Security Considerations
- Passwords stored in plaintext (as per requirement)
- Future: add encryption, environment variables, or external auth service
- Log authentication failures (but not passwords)

## Success Criteria
- Proxy works with authenticated requests
- Unauthenticated requests rejected when auth enabled
- Backward compatibility maintained
- All existing tests pass
- Documentation updated with examples