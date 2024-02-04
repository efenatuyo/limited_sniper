import os, aiohttp, asyncio, time, logging, sys, discord

from .handle      import v_one
from .handle      import v_two
from .handle      import v_three
from .handle      import v_four
from .handle      import v_five
from .cookie      import user_id
from .cookie      import xcrf_token
from .discord_bot import start
from collections import deque
from .cookie.refresh import Bypass

class sniper:
    error_logs: list = deque(maxlen=5)
    total_errors: int = 0
    _total_errors: int = 0
    
    buy_logs: list = []
    total_buys: int = 0
    _total_buys: int = 0
    
    search_logs: list = deque(maxlen=5)
    
    total_searchers: int = 0
    _total_searchers: int = 0
    
    average_speed_v1: list = deque(maxlen=20)
    average_speed_v2: list = deque(maxlen=20)
    average_speed_v3: list = deque(maxlen=20)
    average_speed_v4: list = deque(maxlen=20)
    average_speed_v5: list = deque(maxlen=20)
    
    clear: str = "cls" if os.name == 'nt' else "clear"

    limited_ids: list = []
    
    limited_collectible_ids: list = []
    
    all_limited_collectible_ids: dict = {}
    
    start_time: time.time = time.time()
    _start_time: time.time = time.time()
    
    def __init__(self, data: dict):
        open("logs.txt", "a").write(f"\n                                         ----------------------  MAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] STARTING  ----------------------")
        open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] installing and uninstalling requirements")
        self.check_and_install_modules(["py-cord", "aiohttp"], ["discord.py"])
        self.items = data["items"]
        for item in self.items["list"]:
            if not item.isnumeric():
                raise ValueError("Item Id must be a number not a string")
            
        self.cookie = data["cookie"]
        if data["cookie_unlock"]:
            self.cookie = Bypass(self.cookie).start_process()
        self.account = {"xcsrf_token": asyncio.run(xcrf_token.get(self)), "user_id": asyncio.run(user_id.get(self))}
        
        proxies = data["proxy"]
        self.proxies = []
        for proxy in proxies["proxies"]:
            self.proxies.append(f"{proxies['proxy_type']}://{proxy}")
        
        self.restart_after_config = data["restart_after_config"]
        self.webhook = data["webhook"]
        self.discord_bot = data["discord_bot"]
        if self.discord_bot["enabled"] and not self.discord_bot["authorized_users"]:
            open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] CLOSING FILE. If discord bot is enabled atleast one authorized user is required")
            raise Exception("If discord bot is enabled atleast one authorized user is required")
        self.searches_a_minute = data["requests_a_minute"]
        

    def get_prefix(self):
        if sys.executable.endswith("python.exe"):
            return 'python -m pip'
        elif sys.executable.endswith("py.exe"):
            return 'py -m pip'
        else:
            print("Unable to determine prefix. Please run the script using 'python' or 'py'.")
            
    def check_and_install_modules(self, modules_to_check, uninstall):
        prefix = self.get_prefix()
        if not prefix: return

        installed_modules = os.popen(f'{prefix} freeze').read().split('\n')
        installed_modules = [module.split('==')[0] for module in installed_modules]

        for module in uninstall:
            if module in installed_modules:
                open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] uninstalling {module}")
                os.system(f'{prefix} uninstall -y {module}')
                os.system(f'{prefix} uninstall -y discord')

        for module in modules_to_check:
            if module not in installed_modules:
                open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] installing {module}")
                os.system(f'{prefix} install {module}')
                
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
        logging.getLogger('asyncio').setLevel(logging.CRITICAL)
        session = aiohttp.ClientSession()
        open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] checking proxies")
        await asyncio.gather(*[self.proxy_check(session, proxy) for proxy in self.proxies])
        await session.close()
        while True:
            try:
                tasks = [asyncio.create_task(start(self)) if self.discord_bot["enabled"] else None, asyncio.create_task(v_one.run(self)), asyncio.create_task(v_three.run(self)), asyncio.create_task(v_four.run(self)), asyncio.create_task(v_five.run(self))] + [asyncio.create_task(v_two.run_proxy(self, proxy)) for proxy in self.proxies] + [asyncio.create_task(v_three.run_proxy(self, proxy)) for proxy in self.proxies] + [asyncio.create_task(v_four.run_proxy(self, proxy)) for proxy in self.proxies] + [asyncio.create_task(v_two.run(self)) for i in range(3)]
                await asyncio.gather(*filter(None, tasks))
            except discord.errors.LoginFailure:
                open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] CLOSING FILE. Invalid discord token provided")
                print("Invalid discord token provided...")
                os.system("pause")
                sys.exit(0)
            except Exception as e:
                self.error_logs.append(f"MAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
                open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
                open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] restarting tasks")
                for i, task in enumerate(filter(None, tasks), start=1):
                    open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] cancelling task {i}")
                    task.cancel()
                self._total_errors = 0
                self._total_buys = 0
                self._total_searchers = 0
                self._start_time = time.time()