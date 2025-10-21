"""Constants for Kerbl Welt API."""

# API Configuration
BASE_URL = "https://backend.kerbl-iot.com/api/v0.1"
WEBSOCKET_URL = "wss://backend.kerbl-iot.com/ws/v0.1/socket.io/"

# API Endpoints
ENDPOINT_AUTH_SIGN_IN = "/auth/sign-in"
ENDPOINT_AUTH_REFRESH = "/auth/refresh"
ENDPOINT_USER = "/user"
ENDPOINT_DEVICES = "/device"
ENDPOINT_EVENT_COUNT = "/device/event-count/{device_type}/{device_id}"
ENDPOINT_ADMIN_MESSAGE = "/admin-message/for-user"
ENDPOINT_MAINTENANCE_PING = "/maintenance/ping"
ENDPOINT_MAINTENANCE_BRANCH = "/maintenance/deployed_branch"

# Device Types
DEVICE_TYPE_SMART_SATELLITE = "smart-satellite"
DEVICE_TYPE_SMART_COOP = "smart-coop"
DEVICE_TYPE_SMART_ENERGIZER = "smart-energizer"
DEVICE_TYPE_SMART_MOUSE_TRAP = "smart-mouse-trap"
DEVICE_TYPE_SMART_LIGHT = "smart-light"
DEVICE_TYPE_SMART_WEATHER = "smart-weather"
DEVICE_TYPE_SMART_TRACKER = "smart-tracker"
DEVICE_TYPE_SMART_SOS = "smart-sos"
DEVICE_TYPE_SMART_CHICKEN_DOOR = "smart-chicken-door"
DEVICE_TYPE_SMART_ADS = "smart-ads"

# HTTP Headers
HEADER_AUTHORIZATION = "Authorization"
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_ACCEPT = "Accept"

# Content Types
CONTENT_TYPE_JSON = "application/json"

# Default Timeouts (seconds)
DEFAULT_TIMEOUT = 30
DEFAULT_CONNECT_TIMEOUT = 10

# Token Expiration (approximate, in seconds)
ACCESS_TOKEN_EXPIRY = 15 * 24 * 60 * 60  # ~15 days
REFRESH_TOKEN_EXPIRY = 40 * 24 * 60 * 60  # ~40 days

# Version
__version__ = "0.1.0"
