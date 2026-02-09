import aiohttp
import logging
from .const import BASE_URL

_LOGGER = logging.getLogger(__name__)

class TapElectricAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"X-Api-Key": self.api_key}

    async def get_chargers(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/chargers", headers=self.headers) as resp:
                data = await resp.json() if resp.status == 200 else []
                _LOGGER.debug("Tap Chargers Data: %s", data)
                return data

    async def get_active_sessions(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/charger-sessions", headers=self.headers) as resp:
                data = await resp.json() if resp.status == 200 else []
                _LOGGER.debug("Tap Sessions Data: %s", data)
                return data

    async def set_charging_limit(self, charger_id, amps):
        url = f"{BASE_URL}/chargers/{charger_id}/remote-configuration"
        payload = {"command": "SetChargingProfile", "args": {"limit": float(amps), "unit": "A", "stackLevel": 1, "purpose": "TxProfile"}}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as resp:
                return resp.status == 200

    async def remote_start(self, charger_id):
        url = f"{BASE_URL}/chargers/{charger_id}/remote-control"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"command": "RemoteStartTransaction"}, headers=self.headers) as resp:
                return resp.status == 200

    async def remote_stop(self, charger_id):
        url = f"{BASE_URL}/chargers/{charger_id}/remote-control"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"command": "RemoteStopTransaction"}, headers=self.headers) as resp:
                return resp.status == 200

    async def set_phases(self, charger_id, phase_count):
        url = f"{BASE_URL}/chargers/{charger_id}/remote-configuration"
        payload = {"command": "ChangeConfiguration", "args": {"key": "NumberOfPhases", "value": str(phase_count)}}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as resp:
                return resp.status == 200

    async def set_phases(self, charger_id, phase_count):
        """Wissel tussen 1 en 3 fasen (Geoptimaliseerd voor Alfen)."""
        url = f"{BASE_URL}/chargers/{charger_id}/remote-configuration"
        payload = {
            "command": "ChangeConfiguration",
            "args": {
                "key": "NumberOfPhases",
                "value": str(phase_count)
            }
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=self.headers) as resp:
                    _LOGGER.info("Alfen fase-switch naar %s succesvol: %s", phase_count, resp.status == 200)
                    return resp.status == 200
            except Exception as e:
                _LOGGER.error("Fout bij aanpassen fasen op Alfen: %s", e)
                return False
