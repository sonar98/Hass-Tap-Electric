from homeassistant.components.number import NumberEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for charger in coordinator.data.get("chargers", []):
        entities.append(TapCurrentLimit(coordinator, charger["id"]))
    async_add_entities(entities)

class TapCurrentLimit(NumberEntity):
    def __init__(self, coordinator, charger_id):
        self.coordinator = coordinator
        self.charger_id = charger_id
        self._attr_name = "Tap Laadstroom Limiet"
        self._attr_unique_id = f"tap_current_{charger_id}"
        self._attr_native_min_value = 6
        self._attr_native_max_value = 16
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "A"

    @property
    def native_value(self):
        # Haal de huidige limiet uit de API data indien beschikbaar
        for charger in self.coordinator.data.get("chargers", []):
            if charger["id"] == self.charger_id:
                return charger.get("maxCurrent", 16)
        return 16

    async def set_native_value(self, value):
        """Stuur nieuwe Ampère limiet naar Tap."""
        await self.coordinator.api.set_current_limit(self.charger_id, int(value))
        await self.coordinator.async_request_refresh()
