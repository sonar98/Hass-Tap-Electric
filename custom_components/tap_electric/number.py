from homeassistant.components.number import NumberEntity, NumberDeviceClass
from homeassistant.const import UnitOfElectricCurrent
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for charger in coordinator.data.get("chargers", []):
        entities.append(TapChargingLimit(coordinator, charger))
    async_add_entities(entities)

class TapChargingLimit(NumberEntity):
    _attr_device_class = NumberDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_native_min_value = 6
    _attr_native_max_value = 32
    _attr_native_step = 1

    def __init__(self, coordinator, charger):
        self.coordinator = coordinator
        self.charger_id = charger["id"]
        # Dynamische naamgeving zonder hardcoded strings
        self.charger_name = charger.get("name") or f"Tap Charger {self.charger_id[-4:]}"
        self._attr_name = f"{self.charger_name} Limiet"
        self._attr_unique_id = f"tap_limit_{self.charger_id}"
        self._attr_has_entity_name = False
        
        # We halen de huidige limiet uit de lader-data als die beschikbaar is, 
        # anders gebruiken we 16 als veilige fallback.
        self._attr_native_value = charger.get("maxCurrent") or charger.get("currentLimit") or 16

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.charger_id)},
            "name": self.charger_name,
            "manufacturer": "Tap Electric",
        }

    async def async_set_native_value(self, value):
        """Update de laadstroom naar de API."""
        api = self.coordinator.hass.data[DOMAIN].get("api_instance")
        if api:
            success = await api.set_charging_limit(self.charger_id, value)
            if success:
                self._attr_native_value = value
                # Forceer een refresh van de coordinator zodat alle sensoren direct up-to-date zijn
                await self.coordinator.async_request_refresh()
                self.async_write_ha_state()
