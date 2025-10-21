"""Exceptions for Kerbl Welt API."""


class KerblweltError(Exception):
    """Base exception for Kerbl Welt API errors."""

    pass


class AuthenticationError(KerblweltError):
    """Raised when authentication fails."""

    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid."""

    pass


class TokenExpiredError(AuthenticationError):
    """Raised when access token has expired."""

    pass


class TokenRefreshError(AuthenticationError):
    """Raised when token refresh fails."""

    pass


class APIError(KerblweltError):
    """Raised when API request fails."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code if available
        """
        super().__init__(message)
        self.status_code = status_code


class ConnectionError(KerblweltError):
    """Raised when connection to API fails."""

    pass


class DeviceNotFoundError(KerblweltError):
    """Raised when requested device is not found."""

    def __init__(self, device_id: str) -> None:
        """Initialize device not found error.

        Args:
            device_id: ID of the device that was not found
        """
        super().__init__(f"Device not found: {device_id}")
        self.device_id = device_id


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""

    pass


class ValidationError(KerblweltError):
    """Raised when input validation fails."""

    pass
