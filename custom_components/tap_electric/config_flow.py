
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import aiohttp
from .const import DOMAIN, BASE_URL

class TapElectricConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tap Electric."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Eerste stap als je de integratie toevoegt via de UI."""
        errors = {}
        if user_input is not None:
            api_key = user_input["api_key"]
            
            # Valideer de API-key door de laders op te vragen
            headers = {"X-Api-Key": api_key}
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"{BASE_URL}/chargers", headers=headers) as resp:
                        if resp.status == 200:
                            return self.async_create_entry(title="Tap Electric", data=user_input)
                        else:
                            errors["base"] = "invalid_auth"
                except Exception:
                    errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
            }),
            errors=errors,
        )
