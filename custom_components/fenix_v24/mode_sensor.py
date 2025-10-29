"""Mode sensor entity for Fenix V24 heating zones.

This module contains the FenixModeSensor entity class which represents
the current operating mode for a specific heating zone in a Fenix V24 system.
"""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory

from .api import FenixV24API

_LOGGER = logging.getLogger(__name__)

# Mode mappings based on control_api.py and observed values
MODE_MAPPINGS = {
    "0": "Off",
    "2": "Eco",
    "8": "Eco",
    "11": "Auto",
    "13": "Antifreeze",
    "15": "Manual",
    "16": "Boost",
}


class FenixModeSensor(SensorEntity):
    """Mode sensor entity for a Fenix V24 heating zone.

    This sensor displays the current operating mode for a specific heating zone.
    Modes include: Off, Auto, Manual, Eco, Antifreeze, Boost.

    Attributes:
        _api: FenixV24API client for API communication
        _zone_id: Unique zone identifier
        _zone_label: Human-readable zone name
        _device_id: Device ID for this zone
        _attr_name: Entity name displayed in Home Assistant
        _attr_unique_id: Unique identifier for this entity
        _attr_native_value: Current mode as a string
        _attr_entity_category: Diagnostic category
    """

    def __init__(
        self,
        api: FenixV24API,
        zone_id: str,
        zone_label: str,
        device_id: str | None = None,
    ):
        """Initialize the Fenix V24 mode sensor.

        Args:
            api: FenixV24API client instance for this sensor
            zone_id: Unique zone identifier
            zone_label: Human-readable zone name (e.g., "Living Room")
            device_id: Device ID for this zone (e.g., "C001-000")
        """
        self._api = api
        self._zone_id = zone_id
        self._zone_label = zone_label
        self._device_id = device_id

        # Entity attributes
        self._attr_name = f"Fenix {zone_label} Mode"
        self._attr_unique_id = f"fenix_v24_{api.smarthome_id}_{zone_id}_mode"
        self._attr_icon = "mdi:thermostat"
        self._attr_native_value = None
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        # Store raw mode value for advanced users
        self._raw_mode = None

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        attrs = {}
        if self._raw_mode is not None:
            attrs["raw_mode"] = self._raw_mode
        if self._device_id is not None:
            attrs["device_id"] = self._device_id
        return attrs

    def update(self) -> None:
        """Fetch the latest mode data for this zone.

        Called by Home Assistant on each polling cycle (default 30 seconds).
        This method:
        1. Ensures we have a valid authentication token
        2. Fetches all zone data from the API
        3. Finds this specific zone's data
        4. Extracts the mode from the primary device
        5. Converts raw mode number to human-readable name
        6. Updates the sensor's state

        Note:
            The Fenix V24 API returns mode as 'nv_mode' (new value mode).
            Mode values:
            - 0: Off
            - 2/8: Eco
            - 11: Auto (schedule)
            - 13: Antifreeze
            - 15: Manual
            - 16: Boost

            This is a synchronous function that runs in Home Assistant's
            executor thread pool to avoid blocking the event loop.
        """
        try:
            # Ensure we have a valid authentication token
            self._api.authenticate()

            # Fetch all zones for this smarthome
            zones = self._api.get_zones()

            # Find the data for this specific zone
            for zone_id, zone_data in zones:
                if zone_id == self._zone_id:
                    # Devices can be either a list or dict
                    devices = zone_data.get("devices", [])

                    primary_device = None
                    if isinstance(devices, list) and len(devices) > 0:
                        primary_device = devices[0]
                    elif isinstance(devices, dict):
                        primary_device = devices.get("0", {})

                    if primary_device:
                        # Get the mode value (nv_mode = new value mode)
                        mode_raw = primary_device.get("nv_mode")

                        if mode_raw is not None:
                            self._raw_mode = str(mode_raw)
                            # Convert to human-readable mode
                            self._attr_native_value = MODE_MAPPINGS.get(
                                str(mode_raw), f"Unknown ({mode_raw})"
                            )
                            _LOGGER.debug(
                                f"{self._zone_label} mode: {self._attr_native_value} (raw: {mode_raw})"
                            )
                        break

        except Exception as e:
            _LOGGER.error(f"Failed to update mode sensor {self._zone_label}: {e}")
