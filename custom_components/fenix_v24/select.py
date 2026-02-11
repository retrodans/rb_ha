"""Select platform for Fenix V24 heating system integration.

Creates a mode select entity for each heating zone, allowing users to
view and change the operating mode (Auto, Manual, Off, Antifreeze).
"""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import FenixV24API
from .const import DOMAIN, MODE_MAPPINGS, MODE_NAME_TO_VALUE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fenix V24 mode select entities from a config entry."""
    email = entry.data["email"]
    password = entry.data["password"]
    smarthome_id = entry.data["smarthome_id"]

    api = FenixV24API(email, password, smarthome_id)

    try:
        await hass.async_add_executor_job(api.authenticate)
        zones = await hass.async_add_executor_job(api.get_zones)

        selects = []
        for zone_id, zone_data in zones:
            zone_label = zone_data.get("zone_label", "Unknown")

            device_id = None
            devices = zone_data.get("devices", [])
            if isinstance(devices, list) and len(devices) > 0:
                device_id = devices[0].get("id_device")

            selects.append(FenixModeSelect(api, zone_id, zone_label, device_id))

        async_add_entities(selects, True)
        _LOGGER.info(f"Added {len(selects)} Fenix V24 mode select entities")

    except Exception as e:
        _LOGGER.error(f"Failed to set up Fenix V24 mode selects: {e}")


class FenixModeSelect(SelectEntity):
    """Select entity for controlling a Fenix V24 zone's operating mode."""

    _attr_options = list(MODE_NAME_TO_VALUE.keys())

    def __init__(
        self,
        api: FenixV24API,
        zone_id: str,
        zone_label: str,
        device_id: str | None = None,
    ):
        self._api = api
        self._zone_id = zone_id
        self._zone_label = zone_label
        self._device_id = device_id

        self._attr_name = f"Fenix {zone_label} Mode"
        self._attr_unique_id = f"fenix_v24_{api.smarthome_id}_{zone_id}_mode_select"
        self._attr_icon = "mdi:thermostat"
        self._attr_current_option = None

    @property
    def device_id(self) -> str | None:
        """Return the device ID."""
        return self._device_id

    def update(self) -> None:
        """Fetch the latest mode from the API."""
        try:
            self._api.authenticate()
            zones = self._api.get_zones()

            for zone_id, zone_data in zones:
                if zone_id == self._zone_id:
                    devices = zone_data.get("devices", [])

                    primary_device = None
                    if isinstance(devices, list) and len(devices) > 0:
                        primary_device = devices[0]
                    elif isinstance(devices, dict):
                        primary_device = devices.get("0", {})

                    if primary_device:
                        mode_raw = primary_device.get("nv_mode")
                        if mode_raw is not None:
                            mode_name = MODE_MAPPINGS.get(
                                str(mode_raw), f"Unknown ({mode_raw})"
                            )
                            if mode_name in self._attr_options:
                                self._attr_current_option = mode_name
                            _LOGGER.debug(
                                f"{self._zone_label} mode: {mode_name} (raw: {mode_raw})"
                            )
                    break

        except Exception as e:
            _LOGGER.error(f"Failed to update mode select {self._zone_label}: {e}")

    def select_option(self, option: str) -> None:
        """Change the operating mode."""
        if self._device_id is None:
            _LOGGER.error(f"No device ID for zone {self._zone_label}")
            return

        mode_value = MODE_NAME_TO_VALUE.get(option)
        if mode_value is None:
            _LOGGER.error(f"Unknown mode: {option}")
            return

        self._api.authenticate()
        success = self._api.set_mode(self._device_id, mode_value)

        if success:
            self._attr_current_option = option
            _LOGGER.info(f"Set {self._zone_label} to {option}")
        else:
            _LOGGER.error(f"Failed to set {self._zone_label} to {option}")
