import time, aiohttp, asyncio

from ..lookup import v_three
from ..buy import buy
from . import split_list

async def run(self):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})
    _items = split_list.get(self.limited_collectible_ids, 30)
    while True:
        try:
            for index, _item in enumerate(_items):
                if index > 0:
                    await asyncio.sleep(self.sleep_config["v3_searcher_sleep_in_s"])
                items = await v_three.get(self, _item, session)
                self.total_searchers += len(items)
                for item in items:
                    info = {"price": int(item.get("lowestPrice", 999999999)), "productid_data": item.get("lowestAvailableResaleProductId"), "collectible_item_id": item.get("collectibleItemId"), "item_id": str(item.get("itemTargetId")), "collectible_item_instance_id": item.get("lowestAvailableResaleItemInstanceId")}
                    if not info["item_id"] in self.items["list"]:
                        self.limited_collectible_ids.remove(info["collectible_item_id"])
                    if not item.get("hasResellers"):
                        continue
                    if info['price'] > self.items["list"][info["item_id"]]["max_price"]:
                        continue
                    await buy.purchase(self, info, session)     
        except Exception as e:
            await session.close()
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})  # just to refresh the session
            self.error_logs.append(f"V3 [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
        finally:
            _items = split_list.get(self.limited_collectible_ids, 30)
            await asyncio.sleep(self.sleep_config["v3_searcher_sleep_in_s"])

async def run_proxy(self, proxy):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
    _items = split_list.get(self.limited_collectible_ids, 30)
    while True:
        try:
            for index, _item in enumerate(_items):
                if index > 0:
                    await asyncio.sleep(self.sleep_config["v3_searcher_sleep_in_s"])
                items = await v_three.get(self, _item, session, proxy)
                
                self.total_searchers += len(items)
                print(items + "e")
                for item in items:
                    info = {"price": int(item.get("lowestPrice", 999999999)), "productid_data": item.get("lowestAvailableResaleProductId"), "collectible_item_id": item.get("collectibleItemId"), "item_id": str(item.get("itemTargetId")), "collectible_item_instance_id": item.get("lowestAvailableResaleItemInstanceId")}
                    if not str(item["itemTargetId"]) in self.items["list"]:
                        self.limited_collectible_ids.remove(info["collectible_item_id"])
                    if not item.get("hasResellers"):
                        continue
                    if info['price'] > self.items["list"][str(item["itemTargetId"])]["max_price"]:
                        continue
                    await buy.purchase(self, info, session)     
        except Exception as e:
            await session.close()
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})  # just to refresh the session
            self.error_logs.append(f"V3 [PROXY {proxy}] [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
        finally:
            _items = split_list.get(self.limited_collectible_ids, 30)
            await asyncio.sleep(self.sleep_config["v3_searcher_sleep_in_s"])