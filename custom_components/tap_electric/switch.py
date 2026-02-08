import logging
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    # We halen de api instantie op die we in __init__.py hebben opgeslagen
    api = hass.data[DOMAIN]["api_instance"]
    
    entities = []
    for charger in coordinator.data.get("chargers", []):
        charger_id = charger["id"]
        charger_name = charger.get("name", f"Lader {charger_id[-4:]}")
        
        entities.append(TapStartStopSwitch(api, coordinator, charger_id, charger_name))
        entities.append(TapPhaseSwitch(api, coordinator, charger_id, charger_name))

    async_add_entities(entities)

class TapStartStopSwitch(SwitchEntity):
    """Schakelaar voor Start/Stop actie."""
    def __init__(self, api, coordinator, charger_id, charger_name):
        self._api = api
        self.coordinator = coordinator
        self.charger_id = charger_id
        self._attr_name = f"{charger_name} Start/Stop"
        self._attr_unique_id = f"tap_start_stop_{charger_id}"
        self._attr_icon = "mdi:play-pause"

    @property
    def is_on(self):
        """Geeft aan of er geladen wordt."""
        for c in self.coordinator.data.get("chargers", []):
            if c["id"] == self.charger_id:
                return c.get("status") == "CHARGING"
        return False

    async def async_turn_on(self, **kwargs):
        await self._api.remote_start(self.charger_id)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self._api.remote_stop(self.charger_id)
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.charger_id)}}

class TapPhaseSwitch(SwitchEntity):
    """Schakelaar voor 1-fase (UIT) of 3-fasen (AAN)."""
    def __init__(self, api, coordinator, charger_id, charger_name):
        self._api = api
        self.coordinator = coordinator
        self.charger_id = charger_id
        self._attr_name = f"{charger_name} 3-Fasen Modus"
        self._attr_unique_id = f"tap_phase_switch_{charger_id}"
        self._attr_icon = "mdi:sine-wave"
        self._is_3_phase = True # Default

    @property
    def is_on(self):
        return self._is_3_phase

    async def async_turn_on(self, **kwargs):
        """Naar 3 fasen schakelen."""
        if self._is_charging():
            _LOGGER.warning("Schakelen naar 3 fasen geblokkeerd: Alfen is aan het laden!")
            return

        if await self._api.set_phases(self.charger_id, 3):
            self._is_3_phase = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Naar 1 fase schakelen."""
        if self._is_charging():
            _LOGGER.warning("Schakelen naar 1 fase geblokkeerd: Alfen is aan het laden!")
            return

        if await self._api.set_phases(self.charger_id, 1):
            self._is_3_phase = False
            self.async_write_ha_state()

    def _is_charging(self):
        """Check of de lader momenteel actief is."""
        for c in self.coordinator.data.get("chargers", []):
            if c["id"] == self.charger_id:
                return c.get("status") in ["CHARGING", "SUSPENDED_EV"]
        return False

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.charger_id)}}
