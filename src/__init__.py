import os, aiohttp, asyncio, time

from .handle      import v_one
from .handle      import v_two
from .handle      import v_three
from .handle      import v_four
from .cookie      import user_id
from .cookie      import xcrf_token
from collections import deque

class sniper:
    error_logs: list = deque(maxlen=5)
    buy_logs: list = []
    search_logs: list = deque(maxlen=5)
    
    total_searchers: int = 0
    
    average_speed: list = deque(maxlen=20)

    clear: str = "cls" if os.name == 'nt' else "clear"

    limited_ids: list = []
    
    limited_collectible_ids: list = []
    
    all_limited_collectible_ids: list = []
    
    start_time: time.time = time.time()
    
    def __init__(self, data: dict):
        self.items = data["items"]
        for item in self.items["list"]:
            if not item.isnumeric():
                raise ValueError("Item Id must be a number not a string")
            
        self.cookie = data["cookie"]
        
        self.account = {"xcsrf_token": asyncio.run(xcrf_token.get(self)), "user_id": asyncio.run(user_id.get(self))}
        
        proxies = data["proxy"]
        self.proxies = []
        for proxy in proxies["proxies"]:
            self.proxies.append(f"{proxies['proxy_type']}://{proxy}")
        
        self.sleep_config = data["sleep_config"]
    
    def format_duration(self, duration_seconds):
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        return f"{hours}:{minutes:02}:{seconds:02}"
    
    async def proxy_check(self, session, proxy):
        try:
            async with session.get("https://www.google.com/", proxy=proxy, ssl=False) as rsp:
                if rsp.status != 200:
                    self.proxies.remove(proxy)
        except:
            self.proxies.remove(proxy)
        
    async def run(self):
        session = aiohttp.ClientSession()
        await asyncio.gather(*[self.proxy_check(session, proxy) for proxy in self.proxies])
        await session.close()
        await asyncio.gather(*[v_one.run(self), v_two.run(self), v_three.run(self), v_four.run(self)] + [v_two.run_proxy(self, proxy) for proxy in self.proxies] + [v_three.run_proxy(self, proxy) for proxy in self.proxies])