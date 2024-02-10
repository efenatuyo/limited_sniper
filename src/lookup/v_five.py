from ..cookie import xcrf_token
import time, os, asyncio
async def get(self, collectibleId, session, proxy=None):
    start_time = time.time()
    async with session.get(f"https://apis.roblox.com/marketplace-sales/v1/item/{collectibleId}/resellers?limit=1", headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}}, proxy=proxy, ssl=False) as response:
        if not proxy:
            self.average_speed_v5.append(time.time() - start_time)
        if response.status == 403:
            if (await response.json())['message'] == "Token Validation Failed":
                self.account['xcsrf_token'] = await xcrf_token.get(self)
                raise Exception("Generated new xcrf_token")
        
        if response.status == 429:
            raise Exception("Rate limit exceeded")
        
        try:
            return (await response.json())["data"][0]
        except:
            return {}
        