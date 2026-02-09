from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for charger in coordinator.data.get("chargers", []):
        entities.append(TapStartStopSwitch(coordinator, charger["id"]))
    async_add_entities(entities)

class TapStartStopSwitch(SwitchEntity):
    def __init__(self, coordinator, charger_id):
        self.coordinator = coordinator
        self.charger_id = charger_id
        self._attr_name = "Tap Lader Laden"
        self._attr_unique_id = f"tap_switch_{charger_id}"
        self._attr_device_class = "switch"
        # Optioneel: dit forceert het logo op de switch zelf
        self._attr_entity_picture = "/local/tap_logo.png"

    @property
    def is_on(self):
        # Aan als de status 'CHARGING' of 'SUSPENDEDEVSE' is
        for charger in self.coordinator.data.get("chargers", []):
            if charger["id"] == self.charger_id:
                return charger.get("status") in ["CHARGING", "OCCUPIED", "SUSPENDEDEVSE"]
        return False

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.remote_start(self.charger_id)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.remote_stop(self.charger_id)
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.charger_id)}, "name": "Tap Electric Lader"}
