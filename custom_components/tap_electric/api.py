import aiohttp
from .const import BASE_URL

class TapElectricAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"X-Api-Key": self.api_key}

    async def get_chargers(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/chargers", headers=self.headers) as resp:
                return await resp.json()

    async def get_active_sessions(self):
        """Haal actieve laadsessies op voor Wh en kosten."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/charger-sessions", headers=self.headers) as resp:
                return await resp.json()

    async def set_charging_limit(self, charger_id, amps):
        url = f"{BASE_URL}/chargers/{charger_id}/remote-configuration"
        payload = {"command": "SetChargingProfile", "args": {"limit": float(amps), "unit": "A"}}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as resp:
                return resp.status == 200
