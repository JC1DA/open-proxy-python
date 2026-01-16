"""Configuration settings for the proxy server."""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server configuration
    proxy_host: str = Field(default="0.0.0.0", description="Server bind address")
    proxy_port: int = Field(default=8000, description="Server port")
    log_level: str = Field(default="info", description="Logging level (debug, info, warning, error, critical)")
    debug: bool = Field(default=False, description="Debug mode toggle")

    # CORS configuration
    allowed_origins: List[str] = Field(
        default=["*"],
        description="Comma-separated list of allowed CORS origins"
    )

    # Proxy behavior
    forward_timeout: float = Field(default=30.0, description="Proxy request timeout in seconds")
    max_redirects: int = Field(default=10, description="Maximum number of redirect hops")
    verify_ssl: bool = Field(default=True, description="Whether to verify SSL certificates")

    # Authentication
    auth_enabled: bool = Field(default=False, description="Enable/disable authentication")
    users_file: str = Field(default="config/users.json", description="Path to users configuration file")
    auth_realm: str = Field(default="Open Proxy", description="Authentication realm name")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=False, description="Enable/disable rate limiting")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()