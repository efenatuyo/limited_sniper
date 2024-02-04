from ..cookie import xcrf_token
import time

async def get(self, items, session):
    start_time = time.time()
    async with session.post("https://catalog.roblox.com/v1/catalog/items/details",
                            json={"items": [{"itemType": "Asset", "id": id} for id in items]},
                            headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}},
    ssl=False) as response:
        self.average_speed_v1.append(time.time() - start_time)
        if response.status == 403:
            if (await response.json())['message'] == "Token Validation Failed":
                self.account['xcsrf_token'] = await xcrf_token.get(self)
                raise Exception("Generated new xcrf_token")
        
        if response.status == 429:
            raise Exception("Rate limit exceeded")
        
        return (await response.json())['data']
        
