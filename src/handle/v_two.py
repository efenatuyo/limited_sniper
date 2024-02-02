import time, aiohttp, asyncio

from ..lookup import v_two
from ..buy import buy

async def run(self):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})
    
    while True:
        try:
            for item_id in self.items["list"].copy():
                if item_id in self.limited_ids:
                    continue
                item = await v_two.get(self, item_id, session)
                self.total_searchers += 1
                if not item.get("IsLimited"):
                    info = {"price": item.get("CollectiblesItemDetails", {}).get("CollectibleLowestResalePrice", 9999999), "productid_data": item.get("CollectiblesItemDetails", {}).get("CollectibleLowestAvailableResaleProductId"), "collectible_item_id": item.get("CollectibleItemId"), "item_id": str(item.get("AssetId")), "collectible_item_instance_id": item.get("CollectiblesItemDetails", {}).get("CollectibleLowestAvailableResaleItemInstanceId")} 
                    if not item.get("IsForSale"):
                        del self.items["list"][info['item_id']]
                        continue
                    if info['price'] > self.items["list"][item_id]["max_price"]:
                        continue
                    await buy.purchase(self, info, session)
                else: 
                    self.limited_ids.append(item_id)
               
        except Exception as e:
            await session.close()
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})  # just to refresh the session
            self.error_logs.append(f"V2 [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
            
        finally:
            if self.average_speed:
                await asyncio.sleep(max((60 / 1000) - max(sum(list(self.average_speed)) / len(self.average_speed), 0), 0))

async def run_proxy(self, format_proxy):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
    
    while True:
        try:
            for item_id in self.items["list"].copy():
                if item_id in self.limited_ids:
                    continue
                item = await v_two.get_proxy(item_id, session, format_proxy)
                self.total_searchers += 1
                if not item.get("IsLimited"):
                    info = {"price": item.get("CollectiblesItemDetails", {}).get("CollectibleLowestResalePrice", 9999999), "productid_data": item.get("CollectiblesItemDetails", {}).get("CollectibleLowestAvailableResaleProductId"), "collectible_item_id": item.get("CollectibleItemId"), "item_id": str(item.get("AssetId")), "collectible_item_instance_id": item.get("CollectiblesItemDetails", {}).get("CollectibleLowestAvailableResaleItemInstanceId")} 
                    if not item.get("IsForSale"):
                        del self.items["list"][info['item_id']]
                        continue
                    if info['price'] > self.items["list"][item_id]["max_price"]:
                        continue
                    await buy.purchase(self, info, session)
                else: 
                    self.limited_ids.append(item_id)
               
        except Exception as e:
            await session.close()
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})  # just to refresh the session
            self.error_logs.append(f"V2 [PROXY: {format_proxy}] [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
            
        finally:
            await asyncio.sleep(0.1)