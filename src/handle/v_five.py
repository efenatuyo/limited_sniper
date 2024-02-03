import time, aiohttp, asyncio

from ..buy import buy
from ..lookup import v_five

async def run(self):
    open("logs.txt", "a").write(f"\nV5 [{time.strftime('%H:%M:%S', time.localtime())}] has started up")
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})
    while True:
        try:
            for index, item_id in enumerate(self.limited_collectible_ids):
                if index > 0:
                    await asyncio.sleep(self.sleep_config["v5_searcher_sleep_in_s"])
                item = await v_five.get(self, item_id, session)
                self.total_searchers += 1
                info = {"price": int(item.get("price", 999999999)), "productid_data": item.get("collectibleProductId"), "collectible_item_id": item_id, "item_id": self.all_limited_collectible_ids[item_id], "collectible_item_instance_id": item.get("collectibleItemInstanceId")}
                if info['price'] > self.items["list"][info['item_id']]["max_price"]:
                    continue
                await buy.purchase(self, info, session)
        except asyncio.exceptions.CancelledError:
            await session.close()  
            return
        except Exception as e:
            await session.close()
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})  # just to refresh the session
            self.error_logs.append(f"V5 [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
            open("logs.txt", "a").write(f"\nV5 [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
            self.total_errors += 1
            self._total_errors += 1
        finally:
            await asyncio.sleep(self.sleep_config["v5_searcher_sleep_in_s"])

async def run_proxy(self, proxy):
    open("logs.txt", "a").write(f"\nV5 PROXY [{time.strftime('%H:%M:%S', time.localtime())}] has started up")
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
    while True:
        try:
            for index, item_id in enumerate(self.limited_collectible_ids):
                if index > 0:
                    await asyncio.sleep(self.sleep_config["v5_searcher_sleep_in_s"])
                item = await v_five.get(self, item_id, session, proxy)
                info = {"price": int(item.get("price", 999999999)), "productid_data": item.get("collectibleProductId"), "collectible_item_id": item_id, "item_id": self.all_limited_collectible_ids[item_id], "collectible_item_instance_id": item.get("collectibleItemInstanceId")}
                if info['price'] > self.items["list"][info['item_id']]["max_price"]:
                    continue
                await buy.purchase(self, info, session)
        except asyncio.exceptions.CancelledError:
            await session.close()  
            return
        except Exception as e:
            await session.close()
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})  # just to refresh the session
            self.error_logs.append(f"V5 [PROXY {proxy}] [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
            open("logs.txt", "a").write(f"\nV5 [PROXY {proxy}] [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
            self.total_errors += 1
            self._total_errors += 1
        finally:
            await asyncio.sleep(self.sleep_config["v5_searcher_sleep_in_s"])