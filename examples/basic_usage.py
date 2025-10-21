#!/usr/bin/env python3
"""
Basic usage example for kerblwelt-api library.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from kerblwelt_api import KerblweltClient, InvalidCredentialsError, ConnectionError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Credentials - replace with your actual credentials
EMAIL = "FIXME"
PASSWORD = "FIXME"


async def main() -> None:
    """Main example function."""
    print("=" * 80)
    print("Kerblwelt API Client - Basic Usage Example")
    print("=" * 80)

    try:
        async with KerblweltClient() as client:
            # Authenticate
            print(f"\n1. Authenticating as {EMAIL}...")
            await client.authenticate(EMAIL, PASSWORD)
            print("   ✅ Authentication successful!")

            # Get user information
            print("\n2. Fetching user information...")
            user = await client.get_user()
            print(f"   User ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Language: {user.language}")
            print(f"   Timezone: {user.timezone}")

            # Get devices
            print("\n3. Fetching devices...")
            devices = await client.get_devices()
            print(f"   Found {len(devices)} device(s)")

            # Display device information
            for i, device in enumerate(devices, 1):
                print(f"\n   📡 Device {i}: {device.description}")
                print(f"      ID: {device.id}")
                print(f"      Serial: {device.identifier}")
                print(f"      Brand: {device.brand}")
                print(f"      Online: {'Yes ✅' if device.is_online else 'No ❌'}")
                print(f"      Registered: {device.registered_at.strftime('%Y-%m-%d %H:%M')}")
                print()
                print(f"      Measurements:")
                print(f"        Fence Voltage: {device.fence_voltage}V")
                print(f"        Battery Voltage: {device.battery_voltage}V")
                print(f"        Battery Level: {device.battery_state}%")
                print(f"        Signal Quality: {device.signal_quality}%")
                print()
                print(f"      Status:")
                print(f"        Voltage OK: {'Yes ✅' if device.is_fence_voltage_ok else 'LOW VOLTAGE ⚠️'}")
                print(f"        Battery OK: {'Yes ✅' if not device.is_battery_low else 'LOW BATTERY ⚠️'}")
                print(f"        Alarm Threshold: {device.fence_voltage_alarm_threshold}V")

                # Get event count
                print(f"\n      Fetching event count...")
                event_count = await client.get_device_event_count(device.id)
                print(f"        New Events: {event_count.new}")

            # Demonstrate get_all_device_data
            print("\n4. Fetching all device data efficiently...")
            all_data = await client.get_all_device_data()
            print(f"   Retrieved data for {len(all_data)} device(s) in one call")

            print("\n" + "=" * 80)
            print("✅ Example completed successfully!")
            print("=" * 80)

    except InvalidCredentialsError:
        print("\n❌ Error: Invalid email or password")
    except ConnectionError as e:
        print(f"\n❌ Error: Cannot connect to API - {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
