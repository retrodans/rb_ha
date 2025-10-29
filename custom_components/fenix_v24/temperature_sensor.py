"""Temperature sensor entity for Fenix V24 heating zones.

This module contains the FenixTemperatureSensor entity class which represents
a temperature sensor for a specific heating zone in a Fenix V24 system.
"""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature

from .api import FenixV24API
from .const import TEMP_DIVISOR

_LOGGER = logging.getLogger(__name__)


class FenixTemperatureSensor(SensorEntity):
    """Temperature sensor entity for a Fenix V24 heating zone.

    This sensor represents the current air temperature for a specific heating zone.
    It polls the Fenix V24 API on each update cycle to fetch the latest temperature
    reading from the zone's primary heating device.

    Attributes:
        _api: FenixV24API client for API communication
        _zone_id: Unique zone identifier
        _zone_label: Human-readable zone name
        _attr_name: Entity name displayed in Home Assistant
        _attr_unique_id: Unique identifier for this entity
        _attr_native_unit_of_measurement: Temperature unit (Celsius)
        _attr_device_class: Sensor device class (temperature)
        _attr_state_class: State class for statistics (measurement)
        _attr_native_value: Current temperature reading
    """

    def __init__(
        self,
        api: FenixV24API,
        zone_id: str,
        zone_label: str,
    ):
        """Initialize the Fenix V24 temperature sensor.

        Args:
            api: FenixV24API client instance for this sensor
            zone_id: Unique zone identifier
            zone_label: Human-readable zone name (e.g., "Living Room")
        """
        self._api = api
        self._zone_id = zone_id
        self._zone_label = zone_label

        # Entity attributes
        self._attr_name = f"Fenix {zone_label} Temperature"
        self._attr_unique_id = f"fenix_v24_{api.smarthome_id}_{zone_id}"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_value = None

    def update(self) -> None:
        """Fetch the latest temperature data for this zone.

        Called by Home Assistant on each polling cycle (default 30 seconds).
        This method:
        1. Ensures we have a valid authentication token
        2. Fetches all zone data from the API
        3. Finds this specific zone's data
        4. Extracts temperature from the primary device
        5. Converts temperature from Fahrenheit (API format) to Celsius
        6. Updates the sensor's state

        Note:
            The Fenix V24 API returns temperature in tenths of degrees Fahrenheit.
            Example: temperature_air=720 means 72.0°F = 22.2°C

            This is a synchronous function that runs in Home Assistant's
            executor thread pool to avoid blocking the event loop.
        """
        try:
            # Ensure we have a valid authentication token (uses cached token if available)
            self._api.authenticate()

            # Fetch all zones for this smarthome
            zones = self._api.get_zones()

            # Find the data for this specific zone
            for zone in zones:
                if zone.get("zone_id") == self._zone_id:
                    devices = zone.get("devices", [])
                    if devices and len(devices) > 0:
                        # Use the first device as the primary temperature source
                        primary_device = devices[0]
                        temp_raw = primary_device.get("temperature_air")

                        if temp_raw:
                            # Convert from tenths of Fahrenheit to Celsius
                            # Example: 720 -> 72.0°F -> 22.2°C
                            temp_f = float(temp_raw) / TEMP_DIVISOR
                            temp_c = (temp_f - 32) * 5 / 9
                            self._attr_native_value = round(temp_c, 1)
                            _LOGGER.debug(
                                f"{self._zone_label}: {self._attr_native_value}°C"
                            )
                        break

        except Exception as e:
            _LOGGER.error(f"Failed to update sensor {self._zone_label}: {e}")
