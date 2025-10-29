"""Config flow for Fenix V24 integration.

This module handles the user-facing configuration flow for setting up the Fenix V24
heating system integration. It provides a UI-based configuration wizard that validates
credentials and establishes connectivity before creating the integration.

The config flow:
1. Collects user credentials (email, password, smarthome_id)
2. Validates authentication with the Fenix V24 OAuth2 API
3. Tests API connectivity by retrieving zones
4. Creates a config entry that prevents duplicate configurations
"""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import requests

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    TOKEN_ENDPOINT,
    API_BASE,
    CLIENT_ID,
    OAUTH_GRANT_TYPE,
    OAUTH_SCOPE,
    API_TIMEOUT,
    API_LANGUAGE,
)

_LOGGER = logging.getLogger(__name__)

# Schema for the configuration form shown to users
# Defines the required fields and their types
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("email"): str,
        vol.Required("password"): str,
        vol.Required("smarthome_id"): str,  # Format: <SMARTHOME_ID_FROM_WEBSITE_URL>
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate user credentials and test API connectivity.

    This function performs a two-stage validation:
    1. Authenticates with the Fenix V24 OAuth2 API using email/password
    2. Tests the smarthome_id by attempting to retrieve zones

    Args:
        hass: Home Assistant instance for async executor
        data: User input containing email, password, and smarthome_id

    Returns:
        dict: Configuration entry info including title and zones_count

    Raises:
        InvalidAuth: If authentication fails (invalid credentials)
        CannotConnect: If API is unreachable or smarthome_id is invalid
    """
    email = data["email"]
    password = data["password"]
    smarthome_id = data["smarthome_id"]

    # Test authentication with Keycloak OAuth2
    # This validates the user's email and password
    try:
        token = await hass.async_add_executor_job(
            authenticate, email, password
        )
    except Exception as err:
        _LOGGER.error(f"Authentication failed: {err}")
        raise InvalidAuth from err

    # Test API access with the provided smarthome_id
    # This ensures the smarthome_id is valid and accessible
    try:
        zones = await hass.async_add_executor_job(
            get_zones, token, smarthome_id
        )
        if not zones:
            raise CannotConnect("No zones found for the provided smarthome_id")
    except Exception as err:
        _LOGGER.error(f"Failed to retrieve zones: {err}")
        raise CannotConnect from err

    # Return info for the config entry
    return {
        "title": f"Fenix V24 ({email})",
        "zones_count": len(zones)
    }


def authenticate(email: str, password: str) -> str:
    """Authenticate with Fenix V24 OAuth2 and return access token.

    Uses the OAuth2 password grant flow via Keycloak to obtain an access token.
    This is a synchronous function designed to be called via async_add_executor_job.

    Args:
        email: User's Fenix V24 account email
        password: User's Fenix V24 account password

    Returns:
        str: OAuth2 access token for API requests

    Raises:
        InvalidAuth: If authentication fails (HTTP status != 200)
    """
    # OAuth2 password grant request
    # client_id 'app-front' is the Fenix V24 web application client
    data = {
        "grant_type": OAUTH_GRANT_TYPE,
        "client_id": CLIENT_ID,
        "username": email,
        "password": password,
        "scope": OAUTH_SCOPE,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(TOKEN_ENDPOINT, data=data, headers=headers, timeout=API_TIMEOUT)

    if response.status_code == 200:
        json_response = response.json()
        return json_response["access_token"]
    else:
        raise InvalidAuth(f"Authentication failed: {response.status_code}")


def get_zones(token: str, smarthome_id: str) -> list:
    """Retrieve heating zones from Fenix V24 API.

    Queries the Fenix V24 API to retrieve all configured heating zones for the
    specified smarthome. This validates that the smarthome_id is correct and
    accessible with the authenticated user's token.

    Args:
        token: OAuth2 access token from authenticate()
        smarthome_id: Unique identifier for the smarthome (e.g., <SMARTHOME_ID_FROM_WEBSITE_URL>)

    Returns:
        list: List of zone dictionaries containing zone_id, zone_label, devices, etc.

    Raises:
        CannotConnect: If the API request fails or returns non-200 status
    """
    url = API_BASE + "/smarthome/read/"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "smarthome_id": smarthome_id,
        "lang": API_LANGUAGE,
    }

    response = requests.post(url, data=data, headers=headers, timeout=API_TIMEOUT)

    if response.status_code == 200:
        json_response = response.json()
        return json_response.get("data", {}).get("zones", [])
    else:
        raise CannotConnect(f"Failed to get zones: {response.status_code}")


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Fenix V24 integration.

    This config flow handler manages the user interface for adding a new Fenix V24
    integration to Home Assistant. It collects credentials, validates them, and
    creates the configuration entry.

    Attributes:
        VERSION: Config entry version for future migration support
    """

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial configuration step.

        This is the entry point for the configuration flow. It displays a form to
        collect user credentials, validates them, and creates the config entry.

        The flow prevents duplicate configurations by using the email as a unique ID.

        Args:
            user_input: Form data submitted by the user, or None for initial display

        Returns:
            FlowResult: Either a form to display or a created config entry
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # User has submitted the form, validate the input
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                # API connection or smarthome_id validation failed
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                # Email/password authentication failed
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Validation successful, create the config entry
                # Set unique ID to prevent duplicate entries for the same account
                await self.async_set_unique_id(user_input["email"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input
                )

        # Show the configuration form (initial display or after validation error)
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Exception raised when connection to Fenix V24 API fails.

    This can occur when:
    - The API is unreachable
    - The smarthome_id is invalid or not found
    - Network connectivity issues
    """


class InvalidAuth(HomeAssistantError):
    """Exception raised when authentication credentials are invalid.

    This occurs when:
    - Email address is incorrect or not registered
    - Password is incorrect
    - Account is locked or inactive
    """
