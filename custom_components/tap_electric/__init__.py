import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import TapElectricAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Dit zorgt ervoor dat HA de bestanden sensor.py, number.py en switch.py laadt
PLATFORMS: list[str] = ["sensor", "number", "switch"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tap Electric via config entry."""
    api = TapElectricAPI(entry.data["api_key"])
    
    # Sla de API instantie centraal op voor de switches en de slider
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["api_instance"] = api
    
    async def async_update_data():
        """Data ophalen van de API via de coordinator."""
        try:
            chargers = await api.get_chargers()
            sessions = await api.get_active_sessions()
            
            # We loggen dit even zodat je in de logs kunt zien of er data binnenkomt
            _LOGGER.debug("Data opgehaald voor %s chargers", len(chargers))
            
            return {
                "chargers": chargers,
                "sessions": sessions
            }
        except Exception as err:
            _LOGGER.error("Fout bij ophalen data van Tap Electric: %s", err)
            raise err

    # Maak de coordinator aan (ververst elke 30 seconden)
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Tap Electric",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    # Eerste refresh doen voordat we de platformen starten
    await coordinator.async_config_entry_first_refresh()
    
    # Sla de coordinator op onder het entry_id
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Vertel Home Assistant dat de sensoren, sliders en switches gestart moeten worden
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload een config entry (bij verwijderen of herstarten)."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        # Verwijder ook de API instantie als dit de laatste lader was
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok
