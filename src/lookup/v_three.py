from ..cookie import xcrf_token

async def get(self, items, session, proxy=None):
  while True:
    async with session.post("https://apis.roblox.com/marketplace-items/v1/items/details", json={"itemIds": items}, headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}}, ssl=False, proxy=proxy) as response:
        if response.status == 403:
            if (await response.json())['message'] == "Token Validation Failed":
                self.account['xcsrf_token'] = await xcrf_token.get(self)
                raise Exception("Generated new xcrf_token")
            
        if response.status == 429:
            raise Exception("Rate limit exceeded")
        
        
        if response.status == 500:
            continue
        return await response.json()