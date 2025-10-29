"""Sensor platform for Fenix V24 heating system integration.

This module sets up temperature sensor entities for each heating zone in a Fenix V24
system by coordinating between the API client and sensor entities.

Key features:
- Automatic sensor creation for each discovered zone
- Per-config-entry API client isolation for multi-account support
- Async setup with executor-based API calls
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import FenixV24API
from .const import DOMAIN
from .temperature_sensor import FenixTemperatureSensor

_LOGGER = logging.getLogger(__name__)

# Global API client storage per config entry
# Format: {entry_id: FenixV24API}
# This allows multiple Fenix V24 accounts to be configured simultaneously
_api_clients = {}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fenix V24 temperature sensors from a config entry.

    This function is called by Home Assistant when the integration is loaded.
    It performs the following steps:
    1. Extracts credentials from the config entry
    2. Creates an API client for this config entry
    3. Authenticates with the Fenix V24 API
    4. Retrieves all zones for the smarthome
    5. Creates a temperature sensor entity for each zone

    Args:
        hass: Home Assistant instance
        entry: Config entry containing user credentials
        async_add_entities: Callback to add sensor entities to Home Assistant

    Note:
        This function uses async_add_executor_job to run synchronous API calls
        in the executor thread pool to avoid blocking the event loop.
    """
    email = entry.data["email"]
    password = entry.data["password"]
    smarthome_id = entry.data["smarthome_id"]

    # Create API client for this config entry
    api = FenixV24API(email, password, smarthome_id)
    _api_clients[entry.entry_id] = api

    # Authenticate and get zones from the API
    try:
        # Run synchronous API calls in executor to avoid blocking
        await hass.async_add_executor_job(api.authenticate)
        zones = await hass.async_add_executor_job(api.get_zones)

        # Create a sensor entity for each zone
        _LOGGER.info(f"Processing {len(zones)} zones from API")

        sensors = []
        for idx, zone in enumerate(zones):
            zone_id = zone.get("zone_id")
            zone_label = zone.get("zone_label", "Unknown")
            _LOGGER.info(f"Creating sensor {idx + 1}/{len(zones)}: {zone_label} (ID: {zone_id})")
            sensors.append(FenixTemperatureSensor(api, zone_id, zone_label))

        # Add all sensor entities with update_before_add=True to fetch initial state
        _LOGGER.info(f"Adding {len(sensors)} sensors to Home Assistant")
        async_add_entities(sensors, True)
        _LOGGER.info(f"Successfully set up {len(sensors)} Fenix V24 temperature sensors")

    except Exception as e:
        _LOGGER.error(f"Failed to set up Fenix V24 sensors: {e}")
        # Clean up API client if setup fails
        _api_clients.pop(entry.entry_id, None)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    Cleans up the API client when the integration is unloaded.

    Args:
        hass: Home Assistant instance
        entry: Config entry being unloaded

    Returns:
        bool: True if unload was successful
    """
    # Remove the API client for this entry
    _api_clients.pop(entry.entry_id, None)
    return True
