from ..cookie import xcrf_token
import time

async def get(self, items, session, proxy=None):
    start_time = time.time()
    async with session.post("https://catalog.roblox.com/v1/catalog/items/details",
                            json={"items": [{"itemType": "Asset", "id": id} for id in items]},
                            headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}},
                            proxy=proxy,
    ssl=False) as response:
        if not proxy:
            self.average_speed_v1.append(time.time() - start_time)
        if response.status == 403:
            if (await response.json())['message'] == "Token Validation Failed":
                self.account['xcsrf_token'] = await xcrf_token.get(self)
                raise Exception("Generated new xcrf_token")
        
        if response.status == 429:
            raise Exception("Rate limit exceeded")
        
        return (await response.json())['data']
        
async def get_pp(items, session, proxy):
    async with session.post("https://catalog.roblox.com/v1/catalog/items/details",
                            json={"items": [{"itemType": "Asset", "id": id} for id in items]},
                            headers={"x-csrf-token": await proxy.current_xtt.x_token()},
                            proxy=str(proxy.current),
    ssl=False) as response:
        if response.status == 403:
            if (await response.json())['message'] == "Token Validation Failed":
                await proxy.current_xtt.generate_token(session)
                return []
        elif response.status == 200:
            return (await response.json())['data']
        else:
            return []
        
