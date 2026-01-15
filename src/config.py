"""Configuration settings for the proxy server."""

import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server configuration
    host: str = os.getenv("PROXY_HOST", "0.0.0.0")
    port: int = int(os.getenv("PROXY_PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "info")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS configuration
    allowed_origins: List[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
        if origin.strip()
    ]

    # Proxy behavior
    forward_timeout: float = float(os.getenv("FORWARD_TIMEOUT", "30.0"))
    max_redirects: int = int(os.getenv("MAX_REDIRECTS", "10"))
    verify_ssl: bool = os.getenv("VERIFY_SSL", "true").lower() == "true"

    # Authentication
    auth_enabled: bool = os.getenv("AUTH_ENABLED", "false").lower() == "true"
    users_file: str = os.getenv("USERS_FILE", "config/users.json")
    auth_realm: str = os.getenv("AUTH_REALM", "Open Proxy")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()