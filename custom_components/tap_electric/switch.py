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
        self._attr_name = f"Tap Lader Start/Stop"
        self._attr_unique_id = f"tap_switch_{charger_id}"

    @property
    def is_on(self):
        # Controleer of er een actieve sessie is voor deze lader
        for session in self.coordinator.data.get("sessions", []):
            if session.get("chargerId") == self.charger_id:
                return True
        return False

    async def async_turn_on(self, **kwargs):
        """Start laden."""
        # ConnectorId is bij Alfen meestal 1
        await self.coordinator.api.remote_start(self.charger_id, connector_id=1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Stop laden."""
        await self.coordinator.api.remote_stop(self.charger_id)
        await self.coordinator.async_request_refresh()
