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

from const import (
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
            # Zones are returned as a dict where keys are zone IDs
            zones_dict = json_response.get("data", {}).get("zones", {})
            _LOGGER.info(f"API returned {len(zones_dict)} zones from smarthome {self._smarthome_id}")

            # Convert dict to list of tuples (zone_id, zone_data)
            zones_list = []
            for zone_id, zone_data in zones_dict.items():
                zone_label = zone_data.get("zone_label", "Unknown")
                _LOGGER.info(f"Zone: {zone_label} (ID: {zone_id})")
                zones_list.append((zone_id, zone_data))

            return zones_list
        else:
            _LOGGER.error(f"Failed to get zone data: {response.status_code}")
            return []

    @property
    def smarthome_id(self) -> str:
        """Return the smarthome ID."""
        return self._smarthome_id
