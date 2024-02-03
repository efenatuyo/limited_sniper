from ..cookie import xcrf_token

async def get(self, collectibleId, session, proxy=None):
    async with session.get(f"https://apis.roblox.com/marketplace-sales/v1/item/{collectibleId}/resellers?limit=1", headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}}, proxy=proxy, ssl=False) as response:
        if response.status == 403:
            if (await response.json())['message'] == "Token Validation Failed":
                self.account['xcsrf_token'] = await xcrf_token.get(self)
                raise Exception("Generated new xcrf_token")
        
        if response.status == 429:
            raise Exception("Rate limit exceeded")
        
        return (await response.json())["data"][0]
        