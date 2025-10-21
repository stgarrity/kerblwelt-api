"""Data models for Kerbl Welt API."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class AuthResponse:
    """Authentication response containing tokens."""

    access_token: str
    refresh_token: str


@dataclass
class DeviceType:
    """Device type information."""

    id: str
    name: str


@dataclass
class User:
    """User account information."""

    id: str
    email: str
    language: str
    timezone: str
    device_types: str
    is_test_user: bool
    is_support: bool
    username: str | None = None
    temp_email: str | None = None
    telephone_number: str | None = None
    telephone_number_country_code: str | None = None
    image_uri: str | None = None
    push_notification_sound: str | None = None
    privacy_policy_target: str | None = None
    privacy_policy_current: str | None = None
    terms_of_use_target: str | None = None
    terms_of_use_current: str | None = None
    double_opt_in_confirmed_at: datetime | None = None
    telephone_double_opt_in_confirmed_at: datetime | None = None
    allow_ads: bool = True
    owned_service_group: str | None = None
    roles: list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        """Create User from API response dictionary.

        Args:
            data: API response data

        Returns:
            User instance
        """
        # Parse datetime fields
        double_opt_in = None
        if data.get("doubleOptInConfirmedAt"):
            double_opt_in = datetime.fromisoformat(
                data["doubleOptInConfirmedAt"].replace("Z", "+00:00")
            )

        telephone_opt_in = None
        if data.get("telephoneDoubleOptInConfirmedAt"):
            telephone_opt_in = datetime.fromisoformat(
                data["telephoneDoubleOptInConfirmedAt"].replace("Z", "+00:00")
            )

        return cls(
            id=data["id"],
            email=data["email"],
            language=data["language"],
            timezone=data["timezone"],
            device_types=data["deviceTypes"],
            is_test_user=data["isTestUser"],
            is_support=data["isSupport"],
            username=data.get("username"),
            temp_email=data.get("tempEmail"),
            telephone_number=data.get("telephoneNumber"),
            telephone_number_country_code=data.get("telephoneNumberCountryCode"),
            image_uri=data.get("imageUri"),
            push_notification_sound=data.get("pushNotificationSound"),
            privacy_policy_target=data.get("privacyPolicyTarget"),
            privacy_policy_current=data.get("privacyPolicyCurrent"),
            terms_of_use_target=data.get("termsOfUseTarget"),
            terms_of_use_current=data.get("termsOfUseCurrent"),
            double_opt_in_confirmed_at=double_opt_in,
            telephone_double_opt_in_confirmed_at=telephone_opt_in,
            allow_ads=data.get("allowAds", True),
            owned_service_group=data.get("ownedServiceGroup"),
            roles=data.get("roles", []),
        )


@dataclass
class SmartSatelliteDevice:
    """Smart Satellite electric fence monitor device."""

    id: str
    user_id: str
    description: str
    identifier: str
    registered_at: datetime
    push_notifications: bool
    email_notifications: bool
    email_addresses_notifications: str
    is_online: bool
    timezone: str
    linking_identifier: str
    active: bool
    brand: str
    battery_voltage: float
    fence_voltage: int  # Volts
    mode: int
    fence_voltage_alarm_threshold: int  # Volts
    signal_quality: int  # 0-100%
    battery_state: int  # 0-100%
    current_error: str
    device_type: DeviceType
    offline_since: datetime | None = None
    first_online_at: datetime | None = None
    firmware_version: str | None = None
    target_firmware_version: str | None = None
    firmware_update_state: str | None = None
    firmware_release_date: datetime | None = None
    item_number: str | None = None
    offline_notified: datetime | None = None
    image_uri: str | None = None
    do_desired_and_actual_state_match: bool = True
    mac: str | None = None
    connection_version: str | None = None
    fence_voltage_target: int | None = None
    fence_voltage_alarm_threshold_desired: int | None = None

    @property
    def is_fence_voltage_ok(self) -> bool:
        """Check if fence voltage is above alarm threshold.

        Returns:
            True if voltage is above threshold, False otherwise
        """
        return self.fence_voltage >= self.fence_voltage_alarm_threshold

    @property
    def is_battery_low(self) -> bool:
        """Check if battery is low (below 20%).

        Returns:
            True if battery is below 20%, False otherwise
        """
        return self.battery_state < 20

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SmartSatelliteDevice":
        """Create SmartSatelliteDevice from API response dictionary.

        Args:
            data: API response data

        Returns:
            SmartSatelliteDevice instance
        """
        # Parse datetime fields
        registered_at = datetime.fromisoformat(data["registeredAt"].replace("Z", "+00:00"))

        offline_since = None
        if data.get("offlineSince"):
            offline_since = datetime.fromisoformat(data["offlineSince"].replace("Z", "+00:00"))

        first_online_at = None
        if data.get("firstOnlineAt"):
            first_online_at = datetime.fromisoformat(
                data["firstOnlineAt"].replace("Z", "+00:00")
            )

        offline_notified = None
        if data.get("offlineNotified"):
            offline_notified = datetime.fromisoformat(
                data["offlineNotified"].replace("Z", "+00:00")
            )

        firmware_release_date = None
        if data.get("firmwareReleaseDate"):
            firmware_release_date = datetime.fromisoformat(
                data["firmwareReleaseDate"].replace("Z", "+00:00")
            )

        # Parse device type
        device_type = DeviceType(
            id=data["deviceType"]["id"],
            name=data["deviceType"]["name"],
        )

        return cls(
            id=data["id"],
            user_id=data["userId"],
            description=data["description"],
            identifier=data["identifier"],
            registered_at=registered_at,
            push_notifications=data["pushNotifications"],
            email_notifications=data["emailNotifications"],
            email_addresses_notifications=data["emailAddressesNotifications"],
            is_online=data["isOnline"],
            timezone=data["timezone"],
            linking_identifier=data["linkingIdentifier"],
            active=data["active"],
            brand=data["brand"],
            battery_voltage=data["batteryVoltage"],
            fence_voltage=data["fenceVoltage"],
            mode=data["mode"],
            fence_voltage_alarm_threshold=data["fenceVoltageAlarmThreshold"],
            signal_quality=data["signalQuality"],
            battery_state=data["batteryState"],
            current_error=data["currentError"],
            device_type=device_type,
            offline_since=offline_since,
            first_online_at=first_online_at,
            firmware_version=data.get("firmwareVersion"),
            target_firmware_version=data.get("targetFirmwareVersion"),
            firmware_update_state=data.get("firmwareUpdateState"),
            firmware_release_date=firmware_release_date,
            item_number=data.get("itemNumber"),
            offline_notified=offline_notified,
            image_uri=data.get("imageUri"),
            do_desired_and_actual_state_match=data.get("doDesiredAndActualStateMatch", True),
            mac=data.get("mac"),
            connection_version=data.get("connectionVersion"),
            fence_voltage_target=data.get("fenceVoltageTarget"),
            fence_voltage_alarm_threshold_desired=data.get("fenceVoltageAlarmThresholdDesired"),
        )


@dataclass
class DeviceEventCount:
    """Count of new events for a device."""

    new: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceEventCount":
        """Create DeviceEventCount from API response dictionary.

        Args:
            data: API response data

        Returns:
            DeviceEventCount instance
        """
        return cls(new=data["new"])
