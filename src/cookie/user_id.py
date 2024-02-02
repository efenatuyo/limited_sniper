import aiohttp

async def get(self) -> str:
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})
    response = (await (await session.get("https://users.roblox.com/v1/users/authenticated")).json()).get("id")
    await session.close()
    assert response, "Couldn't scrape user id."
    return response