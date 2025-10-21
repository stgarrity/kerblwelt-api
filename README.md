# Kerblwelt API Client

Python API client for [Kerbl Welt IoT platform](https://app.kerbl-iot.com), which powers the AKO Smart Satellite electric fence monitoring system.

## Features

- **Async/await** support for efficient I/O operations
- **Full type hints** for better IDE support and type checking
- **Automatic token management** with refresh capability
- **Comprehensive error handling** with custom exceptions
- **Data models** using Python dataclasses
- **Well-tested** with pytest

## Installation

```bash
pip install kerblwelt-api
```

Or for development:

```bash
git clone https://github.com/stgarrity/kerblwelt-api
cd kerblwelt-api
pip install -e ".[dev]"
```

## Quick Start

```python
import asyncio
from kerblwelt_api import KerblweltClient

async def main():
    async with KerblweltClient() as client:
        # Authenticate
        await client.authenticate("your-email@example.com", "your-password")

        # Get all devices
        devices = await client.get_devices()

        for device in devices:
            print(f"Device: {device.description}")
            print(f"  Fence Voltage: {device.fence_voltage}V")
            print(f"  Battery: {device.battery_state}%")
            print(f"  Signal: {device.signal_quality}%")
            print(f"  Online: {device.is_online}")
            print(f"  Status: {'OK' if device.is_fence_voltage_ok else 'LOW VOLTAGE!'}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Usage

### Authentication

```python
async with KerblweltClient() as client:
    # Method 1: Authenticate with credentials
    await client.authenticate("email@example.com", "password")

    # Method 2: Restore previous session with tokens
    client.set_tokens(
        access_token="eyJhbGci...",
        refresh_token="eyJhbGci..."
    )
```

### Get User Information

```python
user = await client.get_user()
print(f"User: {user.email}")
print(f"Timezone: {user.timezone}")
print(f"Language: {user.language}")
```

### Get Devices

```python
# Get all Smart Satellite devices
devices = await client.get_devices()

# Get a specific device by ID
device = await client.get_device("device-uuid-here")

# Get device with event count
device_data = await client.get_all_device_data()
for device_id, (device, events) in device_data.items():
    print(f"{device.description}: {events.new} new events")
```

### Access Device Properties

```python
device = devices[0]

# Basic info
print(device.description)      # User-defined name
print(device.id)                # Device UUID
print(device.identifier)        # Serial number

# Status
print(device.is_online)         # Online/offline
print(device.is_fence_voltage_ok)  # Voltage above threshold
print(device.is_battery_low)    # Battery below 20%

# Measurements
print(device.fence_voltage)     # Current voltage (V)
print(device.battery_voltage)   # Battery voltage (V)
print(device.battery_state)     # Battery percentage (0-100)
print(device.signal_quality)    # Signal strength (0-100)

# Thresholds
print(device.fence_voltage_alarm_threshold)  # Alert threshold (V)

# Timestamps
print(device.registered_at)     # Registration date
print(device.first_online_at)   # First connection
print(device.offline_since)     # Last offline time
```

### Token Refresh

The client automatically handles token expiration. You can also manually refresh:

```python
try:
    devices = await client.get_devices()
except TokenExpiredError:
    await client.refresh_token()
    devices = await client.get_devices()
```

### Error Handling

```python
from kerblwelt_api import (
    InvalidCredentialsError,
    DeviceNotFoundError,
    APIError,
    ConnectionError,
)

try:
    await client.authenticate("email@example.com", "wrong-password")
except InvalidCredentialsError:
    print("Invalid email or password")
except ConnectionError:
    print("Cannot connect to Kerbl Welt API")
except APIError as e:
    print(f"API error: {e}")
```

## API Reference

### KerblweltClient

Main client class for interacting with Kerbl Welt API.

**Methods:**

- `authenticate(email: str, password: str) -> None` - Authenticate with credentials
- `set_tokens(access_token: str, refresh_token: str) -> None` - Set tokens manually
- `refresh_token() -> None` - Refresh the access token
- `get_user() -> User` - Get current user information
- `get_devices() -> list[SmartSatelliteDevice]` - Get all Smart Satellite devices
- `get_device(device_id: str) -> SmartSatelliteDevice` - Get specific device
- `get_device_event_count(device_id: str) -> DeviceEventCount` - Get event count
- `get_all_device_data() -> dict` - Get all devices with event counts
- `close() -> None` - Close the client session

**Properties:**

- `is_authenticated: bool` - Check if client is authenticated

### SmartSatelliteDevice

Represents an AKO Smart Satellite electric fence monitor.

**Key Attributes:**

- `id: str` - Device UUID
- `description: str` - User-defined device name
- `fence_voltage: int` - Current fence voltage in volts
- `battery_voltage: float` - Battery voltage in volts
- `battery_state: int` - Battery percentage (0-100)
- `signal_quality: int` - Signal strength (0-100)
- `is_online: bool` - Device online status
- `fence_voltage_alarm_threshold: int` - Alert threshold in volts

**Helper Properties:**

- `is_fence_voltage_ok: bool` - Voltage above threshold
- `is_battery_low: bool` - Battery below 20%

### Exceptions

All exceptions inherit from `KerblweltError`:

- `AuthenticationError` - Base authentication error
  - `InvalidCredentialsError` - Wrong email/password
  - `TokenExpiredError` - Token has expired
  - `TokenRefreshError` - Token refresh failed
- `APIError` - API request failed
- `ConnectionError` - Network connection failed
- `DeviceNotFoundError` - Device ID not found
- `RateLimitError` - API rate limit exceeded
- `ValidationError` - Input validation failed

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/stgarrity/kerblwelt-api
cd kerblwelt-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=kerblwelt_api

# Run specific test file
pytest tests/test_client.py
```

### Code Quality

```bash
# Format code
black kerblwelt_api tests

# Lint code
ruff check kerblwelt_api tests

# Type checking
mypy kerblwelt_api
```

## Requirements

- Python 3.11 or higher
- aiohttp 3.9.0 or higher

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- Built for the [Kerbl Welt IoT platform](https://app.kerbl-iot.com)
- Powers AKO Smart Satellite electric fence monitors
- Designed for integration with Home Assistant

## Links

- [Kerbl Welt Web App](https://app.kerbl-iot.com)
- [AKO Smart Satellite Product Info](https://www.kerbl.com/en/product/ako-smart-satellite/)
- [Home Assistant Integration](https://github.com/stgarrity/homeassistant-kerblwelt)

## Support

For issues and questions:
- [GitHub Issues](https://github.com/stgarrity/kerblwelt-api/issues)
- Email: sgarrity@gmail.com
