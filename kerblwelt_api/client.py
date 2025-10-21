"""Main API client for Kerbl Welt."""

import logging
from typing import Any

import aiohttp

from .auth import AuthManager
from .const import (
    BASE_URL,
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_TIMEOUT,
    DEVICE_TYPE_SMART_SATELLITE,
    ENDPOINT_DEVICES,
    ENDPOINT_EVENT_COUNT,
    ENDPOINT_USER,
)
from .exceptions import APIError, ConnectionError, DeviceNotFoundError
from .models import DeviceEventCount, SmartSatelliteDevice, User

_LOGGER = logging.getLogger(__name__)


class KerblweltClient:
    """Client for interacting with Kerbl Welt API."""

    def __init__(
        self,
        session: aiohttp.ClientSession | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize Kerbl Welt API client.

        Args:
            session: Optional aiohttp client session. If not provided, one will be created.
            timeout: Request timeout in seconds
        """
        self._session = session
        self._own_session = session is None
        self._timeout = timeout
        self._auth: AuthManager | None = None

    async def __aenter__(self) -> "KerblweltClient":
        """Async context manager entry."""
        if self._own_session:
            timeout = aiohttp.ClientTimeout(
                total=self._timeout,
                connect=DEFAULT_CONNECT_TIMEOUT,
            )
            self._session = aiohttp.ClientSession(timeout=timeout)

        self._auth = AuthManager(self._session)  # type: ignore
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the client session."""
        if self._own_session and self._session:
            await self._session.close()
            self._session = None

    @property
    def is_authenticated(self) -> bool:
        """Check if client is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self._auth is not None and self._auth.is_authenticated

    async def authenticate(self, email: str, password: str) -> None:
        """Authenticate with Kerbl Welt API.

        Args:
            email: User email address
            password: User password

        Raises:
            InvalidCredentialsError: If credentials are invalid
            AuthenticationError: If authentication fails
        """
        if not self._auth:
            raise RuntimeError("Client not initialized - use async context manager")

        await self._auth.authenticate(email, password)

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        """Set authentication tokens manually.

        Useful for restoring a previous session.

        Args:
            access_token: Access token
            refresh_token: Refresh token
        """
        if not self._auth:
            raise RuntimeError("Client not initialized - use async context manager")

        self._auth.set_tokens(access_token, refresh_token)

    async def refresh_token(self) -> None:
        """Refresh the access token.

        Raises:
            TokenRefreshError: If token refresh fails
        """
        if not self._auth:
            raise RuntimeError("Client not initialized - use async context manager")

        await self._auth.refresh_access_token()

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make an authenticated API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for aiohttp request

        Returns:
            Response JSON data

        Raises:
            APIError: If API request fails
            ConnectionError: If connection fails
        """
        if not self._session:
            raise RuntimeError("Client not initialized - use async context manager")

        if not self._auth or not self._auth.is_authenticated:
            raise RuntimeError("Not authenticated - call authenticate() first")

        url = f"{BASE_URL}{endpoint}"
        headers = kwargs.pop("headers", {})
        headers.update(self._auth.get_auth_headers())

        _LOGGER.debug("Making %s request to %s", method, endpoint)

        try:
            async with self._session.request(method, url, headers=headers, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 201:
                    return await response.json()
                elif response.status == 401:
                    error_text = await response.text()
                    _LOGGER.error("Unauthorized request to %s: %s", endpoint, error_text)
                    raise APIError(f"Unauthorized: {error_text}", status_code=401)
                elif response.status == 404:
                    error_text = await response.text()
                    _LOGGER.error("Not found: %s - %s", endpoint, error_text)
                    raise APIError(f"Not found: {error_text}", status_code=404)
                elif response.status == 429:
                    error_text = await response.text()
                    _LOGGER.error("Rate limited: %s", error_text)
                    raise APIError(f"Rate limited: {error_text}", status_code=429)
                else:
                    error_text = await response.text()
                    _LOGGER.error(
                        "API request failed with status %d: %s", response.status, error_text
                    )
                    raise APIError(
                        f"API request failed: {error_text}", status_code=response.status
                    )

        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error during request to %s: %s", endpoint, err)
            raise ConnectionError(f"Connection error: {err}") from err

    async def get_user(self) -> User:
        """Get current user information.

        Returns:
            User object with account information

        Raises:
            APIError: If API request fails
        """
        _LOGGER.debug("Fetching user information")
        data = await self._request("GET", ENDPOINT_USER)
        return User.from_dict(data)

    async def get_devices(self) -> list[SmartSatelliteDevice]:
        """Get all Smart Satellite devices for the authenticated user.

        Returns:
            List of SmartSatelliteDevice objects

        Raises:
            APIError: If API request fails
        """
        _LOGGER.debug("Fetching devices")
        data = await self._request("GET", ENDPOINT_DEVICES)

        # Parse Smart Satellite devices
        devices = []
        for device_data in data.get("smartSatellite", []):
            devices.append(SmartSatelliteDevice.from_dict(device_data))

        _LOGGER.info("Found %d Smart Satellite device(s)", len(devices))
        return devices

    async def get_device(self, device_id: str) -> SmartSatelliteDevice:
        """Get a specific Smart Satellite device by ID.

        Args:
            device_id: Device UUID

        Returns:
            SmartSatelliteDevice object

        Raises:
            DeviceNotFoundError: If device is not found
            APIError: If API request fails
        """
        devices = await self.get_devices()

        for device in devices:
            if device.id == device_id:
                return device

        raise DeviceNotFoundError(device_id)

    async def get_device_event_count(self, device_id: str) -> DeviceEventCount:
        """Get event count for a Smart Satellite device.

        Args:
            device_id: Device UUID

        Returns:
            DeviceEventCount object

        Raises:
            APIError: If API request fails
        """
        endpoint = ENDPOINT_EVENT_COUNT.format(
            device_type=DEVICE_TYPE_SMART_SATELLITE,
            device_id=device_id,
        )

        _LOGGER.debug("Fetching event count for device %s", device_id)
        data = await self._request("GET", endpoint)
        return DeviceEventCount.from_dict(data)

    async def get_all_device_data(self) -> dict[str, tuple[SmartSatelliteDevice, DeviceEventCount]]:
        """Get all devices with their event counts.

        Useful for efficient bulk fetching.

        Returns:
            Dictionary mapping device ID to tuple of (device, event_count)

        Raises:
            APIError: If API request fails
        """
        devices = await self.get_devices()
        result = {}

        for device in devices:
            event_count = await self.get_device_event_count(device.id)
            result[device.id] = (device, event_count)

        _LOGGER.info("Fetched data for %d device(s)", len(result))
        return result
