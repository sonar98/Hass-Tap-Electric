import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .api import TapElectricAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Lijst met platforms die we ondersteunen (sensor voor data, number voor de slider)
PLATFORMS = ["sensor", "number"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tap Electric via een config entry."""
    api_key = entry.data["api_key"]
    api = TapElectricAPI(api_key)
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = api

    # Start de sensoren en sliders
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload een config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
