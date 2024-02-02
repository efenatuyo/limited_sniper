from ..cookie import xcrf_token

async def get(self, items, session):
    async with session.post("https://catalog.roblox.com/v1/catalog/items/details",
                            json={"items": [{"itemType": "Asset", "id": id} for id in items]},
                            headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}},
    ssl=False) as response:
        if response.status == 403:
            if (await response.json())['message'] == "Token Validation Failed":
                self.account['xcsrf_token'] = await xcrf_token.get(self)
                raise Exception("Generated new xcrf_token")
        
        if response.status == 429:
            raise Exception("Rate limit exceeded")
        
        return (await response.json())['data']
        
