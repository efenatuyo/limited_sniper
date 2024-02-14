from ..cookie import xcrf_token
import time, os, asyncio
async def get(self, items, session, proxy=None, oth=None):
  while True:
   try:
    start_time = time.time()
    async with session.post("https://apis.roblox.com/marketplace-items/v1/items/details", json={"itemIds": items}, headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}}, ssl=False, proxy=proxy.current if proxy else None) as response:
        if not proxy:
            self.average_speed_v3.append(time.time() - start_time)
        if response.status == 403:
            if (await response.json())['message'] == "Token Validation Failed":
                self.account['xcsrf_token'] = await xcrf_token.get(self)
                raise Exception("Generated new xcrf_token")
            
        if response.status == 429:
            if proxy:
                open("logs.txt", "a").write(f"\nV3 {proxy.current} [{time.strftime('%H:%M:%S', time.localtime())}] Rate limit exceeded")
                self.error_logs.append(f"V3 {proxy.current} [{time.strftime('%H:%M:%S', time.localtime())}] Rate limit exceeded")
                proxy.next()
            raise Exception("Rate limit exceeded")
        
        
        if response.status == 500:
            continue
        return await response.json()
   except:
       return None