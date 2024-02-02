from ..cookie import xcrf_token

async def get(self, item, session, proxy=None):
    async with session.get(f"https://catalog.roblox.com/v1/catalog/items/{item}/details?itemType=Asset",
                            headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}},
    proxy=proxy, ssl=False) as response:
        if response.status == 403:
            if (await response.json())['message'] == "Token Validation Failed":
                self.account['xcsrf_token'] = await xcrf_token.get(self)
                raise Exception("Generated new xcrf_token")
        
        if response.status == 429:
            raise Exception("Rate limit exceeded")
        
        return await response.json()
        