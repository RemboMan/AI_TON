import aiohttp
import config
from typing import Dict, List


class MarketData:
    def __init__(self):
        self.session = None

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def get_dedust_pools(self) -> List[Dict]:
        """Fetch available pools from DeDust"""
        await self.init_session()
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with self.session.get(
                f"{config.DEDUST_API}/pools", timeout=timeout
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # DeDust API returns a list directly
                    if isinstance(data, list):
                        return data
                    # Or it might be wrapped in a dict
                    return data.get("pools", []) if isinstance(data, dict) else []
        except Exception as e:
            print(f"[X] DeDust API error: {e}")
        return []

    async def get_stonfi_pools(self) -> List[Dict]:
        """Fetch available pools from STON.fi"""
        await self.init_session()
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with self.session.get(
                f"{config.STONFI_API}/pools", timeout=timeout
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("pool_list", [])
        except Exception as e:
            print(f"[X] STON.fi API error: {e}")
        return []

    async def get_market_overview(self) -> Dict:
        """Get overview of all markets"""
        dedust_pools = await self.get_dedust_pools()
        stonfi_pools = await self.get_stonfi_pools()

        return {
            "dedust": {
                "pools_count": len(dedust_pools),
                "pools": dedust_pools[:5],  # Top 5
            },
            "stonfi": {
                "pools_count": len(stonfi_pools),
                "pools": stonfi_pools[:5],  # Top 5
            },
        }
