import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

class TapElectricAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.tapelectric.app/v1" # Pas aan naar de juiste Tap URL indien nodig
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    async def get_data(self):
        """Haal alle chargers en actieve sessies op."""
        async with aiohttp.ClientSession() as session:
            try:
                # Ophalen laders
                async with session.get(f"{self.base_url}/chargers", headers=self.headers) as resp:
                    chargers = await resp.json()
                
                # Ophalen actieve sessies
                async with session.get(f"{self.base_url}/sessions", headers=self.headers) as resp:
                    sessions = await resp.json()

                return {
                    "chargers": chargers,
                    "sessions": sessions
                }
            except Exception as e:
                _LOGGER.error("Fout bij ophalen Tap data: %s", e)
                return {"chargers": [], "sessions": []}

    async def remote_start(self, charger_id, connector_id=1):
        """Start het laden."""
        url = f"{self.base_url}/chargers/{charger_id}/remote-start"
        async with aiohttp.ClientSession() as session:
            payload = {"connectorId": connector_id}
            async with session.post(url, headers=self.headers, json=payload) as resp:
                return resp.status == 200

    async def remote_stop(self, charger_id):
        """Stop/Pauzeer het laden."""
        url = f"{self.base_url}/chargers/{charger_id}/remote-stop"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers) as resp:
                return resp.status == 200

    async def set_current_limit(self, charger_id, amps):
        """Stel de Station-MaxCurrent in (werkt met decimalen)."""
        url = f"{self.base_url}/chargers/{charger_id}/settings"
        async with aiohttp.ClientSession() as session:
            payload = {"Station-MaxCurrent": float(amps)}
            async with session.patch(url, headers=self.headers, json=payload) as resp:
                return resp.status == 200

    async def set_phase_limit(self, charger_id, phases):
        """Stel MaxAllowedPhases in (1 of 3)."""
        url = f"{self.base_url}/chargers/{charger_id}/settings"
        async with aiohttp.ClientSession() as session:
            payload = {"MaxAllowedPhases": int(phases)}
            async with session.patch(url, headers=self.headers, json=payload) as resp:
                return resp.status == 200
