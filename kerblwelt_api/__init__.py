"""Python API client for Kerbl Welt IoT platform."""

from .client import KerblweltClient
from .const import __version__
from .exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    DeviceNotFoundError,
    InvalidCredentialsError,
    KerblweltError,
    RateLimitError,
    TokenExpiredError,
    TokenRefreshError,
    ValidationError,
)
from .models import (
    AuthResponse,
    DeviceEventCount,
    DeviceType,
    SmartSatelliteDevice,
    User,
)

__all__ = [
    # Client
    "KerblweltClient",
    # Exceptions
    "KerblweltError",
    "AuthenticationError",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "TokenRefreshError",
    "APIError",
    "ConnectionError",
    "DeviceNotFoundError",
    "RateLimitError",
    "ValidationError",
    # Models
    "AuthResponse",
    "User",
    "DeviceType",
    "SmartSatelliteDevice",
    "DeviceEventCount",
    # Version
    "__version__",
]
