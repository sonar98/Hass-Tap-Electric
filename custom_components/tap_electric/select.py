from homeassistant.components.select import SelectEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for charger in coordinator.data.get("chargers", []):
        entities.append(TapPhaseSelect(coordinator, charger["id"]))
    async_add_entities(entities)

class TapPhaseSelect(SelectEntity):
    def __init__(self, coordinator, charger_id):
        self.coordinator = coordinator
        self.charger_id = charger_id
        self._attr_name = "Maximaal Aantal Fasen"
        self._attr_unique_id = f"tap_phases_{charger_id}"
        self._attr_options = ["1", "3"]

    @property
    def current_option(self):
        for charger in self.coordinator.data.get("chargers", []):
            if charger["id"] == self.charger_id:
                return str(charger.get("MaxAllowedPhases", "3"))
        return "3"

    async def async_select_option(self, option: str):
        await self.coordinator.api.set_phase_limit(self.charger_id, int(option))
        await self.coordinator.async_request_refresh()
