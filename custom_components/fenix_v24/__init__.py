"""The Fenix V24 integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

_LOGGER = logging.getLogger(__name__)

DOMAIN = "fenix_v24"
PLATFORMS: list[Platform] = [Platform.SENSOR]

# Service definitions
SERVICE_SET_BOOST = "set_boost"

SET_BOOST_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Optional("duration_minutes", default=30): vol.All(
            vol.Coerce(int), vol.Range(min=5, max=120)
        ),
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fenix V24 from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_set_boost(call: ServiceCall) -> None:
        """Handle the set_boost service call."""
        entity_id = call.data["entity_id"]
        duration_minutes = call.data.get("duration_minutes", 30)

        # Find the entity
        entity_registry = er.async_get(hass)
        entity_entry = entity_registry.async_get(entity_id)

        if entity_entry is None:
            _LOGGER.error(f"Entity {entity_id} not found")
            return

        # Get the entity from the entity component
        component = hass.data.get("sensor")
        if component is None:
            _LOGGER.error("Sensor component not found")
            return

        entity = component.get_entity(entity_id)
        if entity is None:
            _LOGGER.error(f"Entity {entity_id} not found in sensor component")
            return

        # Check if entity has device_id (is a Fenix sensor)
        if not hasattr(entity, "device_id") or entity.device_id is None:
            _LOGGER.error(f"Entity {entity_id} does not support boost mode")
            return

        # Get the API client
        from .sensor import _api_clients

        api = _api_clients.get(entity_entry.config_entry_id)
        if api is None:
            _LOGGER.error(f"API client not found for entity {entity_id}")
            return

        # Call the boost API
        _LOGGER.info(
            f"Triggering boost for {entity_id} (device {entity.device_id}) for {duration_minutes} minutes"
        )

        result = await hass.async_add_executor_job(
            api.set_boost, entity.device_id, duration_minutes
        )

        if result:
            _LOGGER.info(f"Boost enabled successfully for {entity_id}")
        else:
            _LOGGER.error(f"Failed to enable boost for {entity_id}")

    hass.services.async_register(
        DOMAIN, SERVICE_SET_BOOST, handle_set_boost, schema=SET_BOOST_SCHEMA
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
