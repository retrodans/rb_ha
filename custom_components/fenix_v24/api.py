"""API client for Fenix V24 heating system.

This module handles all communication with the Fenix V24 cloud API, including:
- OAuth2 authentication via Keycloak
- Token management and caching
- Zone data retrieval
"""
from __future__ import annotations

import logging
import requests
from datetime import datetime, timedelta

from .const import (
    TOKEN_ENDPOINT,
    API_BASE,
    CLIENT_ID,
    OAUTH_GRANT_TYPE,
    OAUTH_SCOPE,
    API_TIMEOUT,
    TOKEN_REFRESH_MARGIN,
    API_LANGUAGE,
)

_LOGGER = logging.getLogger(__name__)


class FenixV24API:
    """API client for Fenix V24 heating system.

    Handles authentication, token management, and API requests for a single
    Fenix V24 account. Each instance maintains its own authentication token
    and automatically refreshes it when needed.

    Attributes:
        _email: User's Fenix V24 account email
        _password: User's Fenix V24 account password
        _smarthome_id: Unique smarthome identifier
        _access_token: Current OAuth2 access token
        _refresh_token: OAuth2 refresh token (for future use)
        _token_expires_at: DateTime when the access token expires
    """

    def __init__(self, email: str, password: str, smarthome_id: str):
        """Initialize the Fenix V24 API client.

        Args:
            email: User's Fenix V24 account email
            password: User's Fenix V24 account password
            smarthome_id: Unique smarthome identifier
        """
        self._email = email
        self._password = password
        self._smarthome_id = smarthome_id
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._token_expires_at: datetime | None = None

    def authenticate(self) -> None:
        """Authenticate with Fenix V24 OAuth2 and cache the access token.

        This method implements token caching to avoid unnecessary authentication requests:
        - Checks if a valid cached token exists
        - If cached token is valid, returns immediately
        - If no token or expired, requests a new token
        - Stores token with expiry time (30 seconds before actual expiry for safety)

        Raises:
            Exception: If authentication fails (invalid credentials or API error)

        Note:
            Token refresh is not yet implemented - new token is requested each time.
        """
        # Check if we have a valid cached token
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                _LOGGER.debug("Using cached access token")
                return

        _LOGGER.info("Authenticating with Fenix V24 API...")

        # OAuth2 password grant request
        # client_id 'app-front' is the Fenix V24 web application client
        data = {
            "grant_type": OAUTH_GRANT_TYPE,
            "client_id": CLIENT_ID,
            "username": self._email,
            "password": self._password,
            "scope": OAUTH_SCOPE,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(
            TOKEN_ENDPOINT, data=data, headers=headers, timeout=API_TIMEOUT
        )

        if response.status_code == 200:
            json_response = response.json()
            self._access_token = json_response["access_token"]
            self._refresh_token = json_response["refresh_token"]
            expires_in = json_response["expires_in"]
            # Set expiry margin to ensure token is always valid
            self._token_expires_at = datetime.now() + timedelta(
                seconds=expires_in - TOKEN_REFRESH_MARGIN
            )
            _LOGGER.info(f"Authentication successful, token expires in {expires_in} seconds")
        else:
            _LOGGER.error(
                f"Authentication failed: {response.status_code} - {response.text}"
            )
            raise Exception("Authentication failed")

    def get_zones(self) -> list:
        """Retrieve heating zone data from the Fenix V24 API.

        Queries the Fenix V24 API to get all zones configured for this smarthome.
        The API returns zones as a dictionary where keys are zone IDs.
        Each zone contains information about:
        - zone_label: Human-readable name (e.g., "Living Room")
        - devices: Dictionary of heating devices in the zone with temperature data

        Returns:
            list: List of tuples (zone_id, zone_data), or empty list if request fails

        Raises:
            Exception: If no access token is available (not authenticated)
        """
        if not self._access_token:
            raise Exception("Not authenticated")

        url = API_BASE + "/smarthome/read/"

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "smarthome_id": self._smarthome_id,
            "lang": API_LANGUAGE,  # Language for zone labels and error messages
        }

        response = requests.post(url, data=data, headers=headers, timeout=API_TIMEOUT)

        if response.status_code == 200:
            json_response = response.json()
            # Zones can be returned as either a list or dict depending on API version
            zones_raw = json_response.get("data", {}).get("zones", [])

            _LOGGER.info(f"API returned {len(zones_raw) if isinstance(zones_raw, (list, dict)) else 0} zones from smarthome {self._smarthome_id}")

            # Convert to list of tuples (zone_id, zone_data)
            zones_list = []

            if isinstance(zones_raw, list):
                # API returns zones as a list with 'num_zone' field
                for zone_data in zones_raw:
                    zone_id = str(zone_data.get("num_zone", "unknown"))
                    zone_label = zone_data.get("zone_label", "Unknown")
                    _LOGGER.info(f"Zone: {zone_label} (ID: {zone_id})")
                    zones_list.append((zone_id, zone_data))

            elif isinstance(zones_raw, dict):
                # API returns zones as dict where keys are zone IDs
                for zone_id, zone_data in zones_raw.items():
                    zone_label = zone_data.get("zone_label", "Unknown")
                    _LOGGER.info(f"Zone: {zone_label} (ID: {zone_id})")
                    zones_list.append((zone_id, zone_data))

            else:
                _LOGGER.warning(f"API returned zones as unexpected type: {type(zones_raw).__name__}")

            return zones_list
        else:
            _LOGGER.error(f"Failed to get zone data: {response.status_code}")
            return []

    def set_boost(self, device_id: str, duration_minutes: int = 30) -> bool:
        """Enable boost mode for a device.

        Args:
            device_id: Device ID (e.g., "C001-000")
            duration_minutes: Duration in minutes (default 30)

        Returns:
            bool: True if successful, False otherwise

        Note:
            This sets the device to manual mode with the boost temperature
            setpoint for the specified duration. The actual boost implementation
            may vary - test carefully!
        """
        if not self._access_token:
            raise Exception("Not authenticated")

        url = API_BASE + "/query/push/"

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Convert minutes to seconds
        duration_seconds = duration_minutes * 60

        # Build the query to enable boost mode
        # Mode 16 appears to be boost mode based on zone data (nv_mode: '16')
        # We'll try setting time_boost and using the consigne_boost setpoint
        data = {
            "token": self._access_token,
            "smarthome_id": self._smarthome_id,
            "context": "1",
            "query[id_device]": device_id,
            "query[time_boost]": str(duration_seconds),
            "query[gv_mode]": "16",  # Boost mode
            "query[nv_mode]": "16",
        }

        _LOGGER.info(f"Setting boost mode for device {device_id} for {duration_minutes} minutes")

        try:
            response = requests.post(url, data=data, headers=headers, timeout=API_TIMEOUT)

            if response.status_code == 200:
                _LOGGER.info(f"Successfully enabled boost for device {device_id}")
                return True
            else:
                _LOGGER.error(f"Failed to set boost: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            _LOGGER.error(f"Exception setting boost: {e}")
            return False

    @property
    def smarthome_id(self) -> str:
        """Return the smarthome ID."""
        return self._smarthome_id
