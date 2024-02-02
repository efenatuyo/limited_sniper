import aiohttp

async def get(self):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})
    response = (await session.post("https://economy.roblox.com/")).headers.get("x-csrf-token")
    await session.close()
    assert response, "Failed to get x-csrf-token"
    return response