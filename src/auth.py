"""Authentication module for proxy server."""

import json
import logging
import base64
from typing import Dict, Optional, Tuple

from .config import settings

logger = logging.getLogger(__name__)


class UserManager:
    """Manages user credentials loaded from a JSON file."""

    def __init__(self, users_file: str) -> None:
        self.users_file = users_file
        self.users: Dict[str, str] = {}
        self._load_users()

    def _load_users(self) -> None:
        """Load users from JSON file."""
        try:
            with open(self.users_file, "r") as f:
                self.users = json.load(f)
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
        stored_password = self.users.get(username)
        if stored_password is None:
            logger.debug("User %s not found", username)
            return False
        if stored_password != password:
            logger.debug("Invalid password for user %s", username)
            return False
        logger.debug("Authentication successful for user %s", username)
        return True


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
def get_user_manager() -> UserManager:
    """Create or return a UserManager instance."""
    if not hasattr(get_user_manager, "_instance"):
        get_user_manager._instance = UserManager(settings.users_file)
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