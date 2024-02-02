from ..cookie import xcrf_token


async def get(self, collectible_item_id, session):
    async with session.get(f"https://apis.roblox.com/marketplace-sales/v1/item/{collectible_item_id}/resellers?limit=1",
                           headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}},
    ssl=False) as response:
        if response.status == 403:
            if (await response.json())['message'] == "Token Validation Failed":
                self.account['xcsrf_token'] = await xcrf_token(self)
                raise Exception("Generated new xcrf_token")
        
        if response.status == 429:
            raise Exception("Rate limit exceeded")
        
        return (await response.json())["data"][0]

async def get_limited(self, itemId, session):
    async with session.get(f"https://economy.roblox.com/v1/assets/{itemId}/resellers",
                           headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}},
    ssl=False) as response:
        if response.status == 403:
            if (await response.json())['message'] == "Token Validation Failed":
                self.account['xcsrf_token'] = await xcrf_token(self)
                raise Exception("Generated new xcrf_token")
        
        if response.status == 429:
            raise Exception("Rate limit exceeded")
        
        return (await response.json())["data"][0]