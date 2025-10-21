"""Authentication module for Kerbl Welt API."""

import logging
from typing import Any

import aiohttp

from .const import (
    BASE_URL,
    CONTENT_TYPE_JSON,
    ENDPOINT_AUTH_REFRESH,
    ENDPOINT_AUTH_SIGN_IN,
    HEADER_AUTHORIZATION,
    HEADER_CONTENT_TYPE,
)
from .exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    TokenExpiredError,
    TokenRefreshError,
)
from .models import AuthResponse

_LOGGER = logging.getLogger(__name__)


class AuthManager:
    """Manages authentication with Kerbl Welt API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize authentication manager.

        Args:
            session: aiohttp client session
        """
        self._session = session
        self._access_token: str | None = None
        self._refresh_token: str | None = None

    @property
    def access_token(self) -> str | None:
        """Get current access token.

        Returns:
            Access token or None if not authenticated
        """
        return self._access_token

    @property
    def refresh_token(self) -> str | None:
        """Get current refresh token.

        Returns:
            Refresh token or None if not authenticated
        """
        return self._refresh_token

    @property
    def is_authenticated(self) -> bool:
        """Check if currently authenticated.

        Returns:
            True if access token is available
        """
        return self._access_token is not None

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests.

        Returns:
            Dictionary with Authorization header

        Raises:
            AuthenticationError: If not authenticated
        """
        if not self._access_token:
            raise AuthenticationError("Not authenticated - access token not available")

        return {HEADER_AUTHORIZATION: f"Bearer {self._access_token}"}

    async def authenticate(self, email: str, password: str) -> AuthResponse:
        """Authenticate with email and password.

        Args:
            email: User email address
            password: User password

        Returns:
            AuthResponse containing access and refresh tokens

        Raises:
            InvalidCredentialsError: If credentials are invalid
            AuthenticationError: If authentication fails for other reasons
        """
        url = f"{BASE_URL}{ENDPOINT_AUTH_SIGN_IN}"
        payload = {"email": email, "password": password}
        headers = {HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON}

        _LOGGER.debug("Authenticating user: %s", email)

        try:
            async with self._session.post(url, json=payload, headers=headers) as response:
                if response.status == 201:
                    data = await response.json()
                    self._access_token = data["accessToken"]
                    self._refresh_token = data["refreshToken"]

                    _LOGGER.info("Authentication successful for user: %s", email)

                    return AuthResponse(
                        access_token=self._access_token,
                        refresh_token=self._refresh_token,
                    )
                elif response.status == 401:
                    _LOGGER.error("Invalid credentials for user: %s", email)
                    raise InvalidCredentialsError("Invalid email or password")
                else:
                    error_text = await response.text()
                    _LOGGER.error(
                        "Authentication failed with status %d: %s", response.status, error_text
                    )
                    raise AuthenticationError(f"Authentication failed: {error_text}")

        except aiohttp.ClientError as err:
            _LOGGER.error("Network error during authentication: %s", err)
            raise AuthenticationError(f"Network error during authentication: {err}") from err

    async def refresh_access_token(self) -> AuthResponse:
        """Refresh access token using refresh token.

        Returns:
            AuthResponse with new access and refresh tokens

        Raises:
            TokenRefreshError: If token refresh fails
            AuthenticationError: If no refresh token is available
        """
        if not self._refresh_token:
            raise AuthenticationError("No refresh token available")

        url = f"{BASE_URL}{ENDPOINT_AUTH_REFRESH}"
        payload = {"refreshToken": self._refresh_token}
        headers = {HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON}

        _LOGGER.debug("Refreshing access token")

        try:
            async with self._session.post(url, json=payload, headers=headers) as response:
                if response.status == 201:
                    data = await response.json()
                    self._access_token = data["accessToken"]
                    self._refresh_token = data["refreshToken"]

                    _LOGGER.info("Token refresh successful")

                    return AuthResponse(
                        access_token=self._access_token,
                        refresh_token=self._refresh_token,
                    )
                elif response.status == 401:
                    _LOGGER.error("Refresh token expired or invalid")
                    self._access_token = None
                    self._refresh_token = None
                    raise TokenExpiredError("Refresh token expired - re-authentication required")
                else:
                    error_text = await response.text()
                    _LOGGER.error("Token refresh failed with status %d: %s", response.status, error_text)
                    raise TokenRefreshError(f"Token refresh failed: {error_text}")

        except aiohttp.ClientError as err:
            _LOGGER.error("Network error during token refresh: %s", err)
            raise TokenRefreshError(f"Network error during token refresh: {err}") from err

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        """Manually set authentication tokens.

        Useful for restoring a previous session.

        Args:
            access_token: Access token
            refresh_token: Refresh token
        """
        self._access_token = access_token
        self._refresh_token = refresh_token
        _LOGGER.debug("Tokens set manually")

    def clear_tokens(self) -> None:
        """Clear stored authentication tokens."""
        self._access_token = None
        self._refresh_token = None
        _LOGGER.debug("Tokens cleared")
