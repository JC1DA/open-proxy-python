"""Authentication module for proxy server."""

import json
import logging
import base64
from typing import Any, Dict, Optional, Tuple

from .config import settings

logger = logging.getLogger(__name__)

# Default rate limits
DEFAULT_RATE_LIMIT_PER_MINUTE = 60
DEFAULT_RATE_LIMIT_PER_MONTH = 10000


class UserManager:
    """Manages user credentials and rate limits loaded from a JSON file."""

    def __init__(self, users_file: str) -> None:
        self.users_file = users_file
        self.users: Dict[str, Dict[str, Any]] = {}
        self._load_users()

    def _load_users(self) -> None:
        """Load users from JSON file."""
        try:
            with open(self.users_file, "r") as f:
                raw_users = json.load(f)
            
            # Process users - support both old and new format
            for username, data in raw_users.items():
                if isinstance(data, str):
                    # Old format: "username": "password"
                    self.users[username] = {
                        "password": data,
                        "rate_limit_per_minute": DEFAULT_RATE_LIMIT_PER_MINUTE,
                        "rate_limit_per_month": DEFAULT_RATE_LIMIT_PER_MONTH,
                    }
                elif isinstance(data, dict):
                    # New format: "username": {"password": "...", "rate_limit_per_minute": X, ...}
                    self.users[username] = {
                        "password": data.get("password", ""),
                        "rate_limit_per_minute": data.get("rate_limit_per_minute", DEFAULT_RATE_LIMIT_PER_MINUTE),
                        "rate_limit_per_month": data.get("rate_limit_per_month", DEFAULT_RATE_LIMIT_PER_MONTH),
                    }
                else:
                    logger.warning("Invalid user data format for user %s", username)
            
            logger.info("Loaded %d users from %s", len(self.users), self.users_file)
        except FileNotFoundError:
            logger.warning("Users file %s not found, no users loaded", self.users_file)
            self.users = {}
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in %s: %s", self.users_file, e)
            self.users = {}
        except Exception as e:
            logger.error("Error loading users file %s: %s", self.users_file, e)
            self.users = {}

    def validate_credentials(self, username: str, password: str) -> bool:
        """Validate username and password."""
        if not self.users:
            logger.warning("No users loaded, authentication disabled")
            return False
        
        user_data = self.users.get(username)
        if user_data is None:
            logger.debug("User %s not found", username)
            return False
        
        stored_password = user_data.get("password", "")
        if stored_password != password:
            logger.debug("Invalid password for user %s", username)
            return False
        
        logger.debug("Authentication successful for user %s", username)
        return True

    def get_user_rate_limits(self, username: str) -> Tuple[int, int]:
        """Get rate limits for a user.
        
        Returns:
            Tuple of (per_minute, per_month)
        """
        user_data = self.users.get(username)
        if user_data is None:
            return DEFAULT_RATE_LIMIT_PER_MINUTE, DEFAULT_RATE_LIMIT_PER_MONTH
        
        return (
            user_data.get("rate_limit_per_minute", DEFAULT_RATE_LIMIT_PER_MINUTE),
            user_data.get("rate_limit_per_month", DEFAULT_RATE_LIMIT_PER_MONTH),
        )

    def user_exists(self, username: str) -> bool:
        """Check if a user exists."""
        return username in self.users


class BasicAuthParser:
    """Parse Basic Authentication header."""

    @staticmethod
    def parse_header(header: str) -> Optional[Tuple[str, str]]:
        """Parse 'Proxy-Authorization: Basic <credentials>' header.
        
        Returns (username, password) or None if invalid.
        """
        if not header:
            return None
        try:
            scheme, credentials = header.split(" ", 1)
            if scheme.lower() != "basic":
                return None
            decoded = base64.b64decode(credentials).decode("utf-8")
            username, password = decoded.split(":", 1)
            return username, password
        except (ValueError, UnicodeDecodeError):
            return None


# Global instances
def _resolve_users_file() -> str:
    """Resolve the users file path to an absolute path.
    
    Handles both relative and absolute paths, and paths relative to the project root.
    """
    import os
    users_file = settings.users_file
    
    # If it's already an absolute path, return as-is
    if os.path.isabs(users_file):
        return users_file
    
    # If the file exists in the current working directory, use that
    if os.path.exists(users_file):
        return os.path.abspath(users_file)
    
    # Try to resolve relative to the project root (where this package is located)
    package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_path = os.path.join(package_dir, users_file)
    if os.path.exists(project_path):
        return project_path
    
    # Fall back to the original path (will trigger file not found warning)
    return users_file


def get_user_manager() -> UserManager:
    """Create or return a UserManager instance."""
    if not hasattr(get_user_manager, "_instance"):
        resolved_path = _resolve_users_file()
        logger.debug("Loading users from: %s", resolved_path)
        get_user_manager._instance = UserManager(resolved_path)
    return get_user_manager._instance


def authenticate_request(auth_header: Optional[str]) -> bool:
    """Authenticate a request using Basic Authentication."""
    if not settings.auth_enabled:
        return True
    
    if not auth_header:
        logger.warning("Authentication required but no header provided")
        return False
    
    credentials = BasicAuthParser.parse_header(auth_header)
    if not credentials:
        logger.warning("Invalid authentication header")
        return False
    
    username, password = credentials
    user_manager = get_user_manager()
    return user_manager.validate_credentials(username, password)


def get_authenticated_username(auth_header: Optional[str]) -> Optional[str]:
    """Get username from authentication header if valid.
    
    Returns the username if authentication is successful, None otherwise.
    """
    if not settings.auth_enabled:
        return None
    
    if not auth_header:
        return None
    
    credentials = BasicAuthParser.parse_header(auth_header)
    if not credentials:
        return None
    
    username, password = credentials
    user_manager = get_user_manager()
    
    if user_manager.validate_credentials(username, password):
        return username
    
    return None
