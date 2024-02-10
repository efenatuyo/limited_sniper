from ..cookie import xcrf_token
import time

async def get(self, item, session, proxy=None):
    start_time = time.time()
    async with session.get(f"https://economy.roblox.com/v2/assets/{item}/details",
                           headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}},
                           proxy=proxy,
    ssl=False) as response:
        if not proxy:
            self.average_speed_v2.append((time.time() - start_time) / 3)
        if response.status == 403:
            if (await response.json())['message'] == "Token Validation Failed":
                self.account['xcsrf_token'] = await xcrf_token.get(self)
                raise Exception("Generated new xcrf_token")
            
        if response.status == 429:
            return
        
        return await response.json()
