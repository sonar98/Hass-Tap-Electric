from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    
    # Verwerk Chargers
    for charger in coordinator.data.get("chargers", []):
        c_id = charger.get("id", "unknown")
        c_name = charger.get("name") or f"Tap Lader {c_id[-4:]}"
        
        for key, value in charger.items():
            if isinstance(value, (int, float, str)) and key != "id":
                entities.append(TapDynamicSensor(coordinator, c_id, c_name, key, "charger"))

    # Verwerk Sessies (Nu met Unieke IDs per sessie!)
    for session in coordinator.data.get("sessions", []):
        # We gebruiken het echte Sessie ID om duplicaten te voorkomen
        s_id = session.get("id", "unknown_sess")
        c_id = session.get("chargerId") or "unlinked"
        
        for key, value in session.items():
            if isinstance(value, (int, float, str)) and key != "id":
                # We voegen het s_id toe aan de unieke ID van de sensor
                entities.append(TapDynamicSensor(coordinator, c_id, f"Sessie {s_id[-4:]}", key, f"session_{s_id}"))

    async_add_entities(entities)

class TapDynamicSensor(SensorEntity):
    def __init__(self, coordinator, charger_id, charger_name, key, source_id):
        self.coordinator = coordinator
        self.charger_id = charger_id
        self.charger_name = charger_name
        self.key = key
        self.source_id = source_id
        self._attr_name = f"{charger_name} {key.replace('_', ' ').capitalize()}"
        # De unique_id bevat nu het specifieke sessie-ID (source_id)
        self._attr_unique_id = f"tap_{source_id}_{key}"
        self._attr_has_entity_name = False

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        
        # Zoek in chargers
        if "session" not in self.source_id:
            for c in self.coordinator.data.get("chargers", []):
                if c.get("id") == self.charger_id:
                    return c.get(self.key)
        # Zoek in specifieke sessie
        else:
            actual_sess_id = self.source_id.replace("session_", "")
            for s in self.coordinator.data.get("sessions", []):
                if s.get("id") == actual_sess_id:
                    return s.get(self.key)
        return None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.charger_id)},
            "name": "Tap Electric Lader",
            "manufacturer": "Tap Electric",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
