import time, aiohttp, asyncio, random

from ..lookup import v_two

async def run(self):
    open("logs.txt", "a").write(f"\nV2 [{time.strftime('%H:%M:%S', time.localtime())}] has started up")
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})
    
    while True:
        try:
            lis = list(self.items["list"].copy())
            random.shuffle(lis)
            for i, item_id in enumerate(lis):
                if i > 0:
                    if self.average_speed_v2:
                        await asyncio.sleep(max((60 / 1000) - max(sum(list(self.average_speed_v2)) / len(self.average_speed_v2), 0), 0))      
                if not item_id in self.items["list"]:
                    continue
                item = await v_two.get(self, item_id, session)
                if not item: continue
                self.total_searchers += 1
                self._total_searchers += 1
                if not item.get("IsLimited") and not item.get("IsLimitedUnique"):
                    if not item.get("CollectiblesItemDetails"):
                        continue 
                    info = {"price": item.get("CollectiblesItemDetails", {}).get("CollectibleLowestResalePrice", 9999999), "productid_data": item.get("CollectiblesItemDetails", {}).get("CollectibleLowestAvailableResaleProductId"), "collectible_item_id": item.get("CollectibleItemId"), "item_id": str(item.get("AssetId")), "collectible_item_instance_id": item.get("CollectiblesItemDetails", {}).get("CollectibleLowestAvailableResaleItemInstanceId")} 
                    if not info['price']:
                        continue 
                    if not item.get("IsForSale"):
                        if item_id in self.items["list"]:
                            del self.items["list"][item_id]
                        continue
                    if info['price'] > self.items["list"][item_id]["max_price"]:
                        continue
                    await self.purchase(info, session)
                elif item.get("IsLimited") or item.get("IsLimitedUnique"):
                    self.limited_ids.append(item_id)
    
        except asyncio.exceptions.CancelledError:
            await session.close()
            return
        except Exception as e:
            await session.close()
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})  # just to refresh the session
            self.error_logs.append(f"V2 [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
            open("logs.txt", "a").write(f"\nV2 [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
            self.total_errors += 1
            self._total_errors += 1
            
        finally:
            if self.average_speed_v2:
                await asyncio.sleep(max((60 / 1000) - max(sum(list(self.average_speed_v2)) / len(self.average_speed_v2), 0), 0))

                
async def run_proxy(self, format_proxy):
    open("logs.txt", "a").write(f"\nV2 PROXY [{time.strftime('%H:%M:%S', time.localtime())}] has started up")
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
    
    while True:
        try:
            lis = list(self.items["list"].copy().keys())
            random.shuffle(lis)
            self.items["list"] = {key: self.items["list"][key] for key in lis}
            for i, item_id in enumerate(self.items["list"].copy()):
                if i > 0:
                    await asyncio.sleep(0.1)
                if not item_id in self.items["list"]:
                    continue
                item = await v_two.get(self, item_id, session, format_proxy)
                if not item: continue
                self.total_searchers += 1
                self._total_searchers += 1
                if not item.get("IsLimited") and not item.get("IsLimitedUnique"):
                    if not item.get("CollectiblesItemDetails"):
                        continue 
                    info = {"price": item.get("CollectiblesItemDetails", {}).get("CollectibleLowestResalePrice", 9999999), "productid_data": item.get("CollectiblesItemDetails", {}).get("CollectibleLowestAvailableResaleProductId"), "collectible_item_id": item.get("CollectibleItemId"), "item_id": str(item.get("AssetId")), "collectible_item_instance_id": item.get("CollectiblesItemDetails", {}).get("CollectibleLowestAvailableResaleItemInstanceId")} 
                    if not info['price']: continue
                    if not item.get("IsForSale"):
                        if info['item_id'] in self.items["list"]:
                            del self.items["list"][info['item_id']]
                        continue
                    if info['price'] > self.items["list"][item_id]["max_price"]:
                        continue
                    await self.purchase(info, session)
                elif item.get("IsLimited") or item.get("IsLimitedUnique"): 
                    self.limited_ids.append(item_id)
        except asyncio.exceptions.CancelledError:
            await session.close()      
            return 
        except Exception as e:
            await session.close()
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
            self.error_logs.append(f"V2 [PROXY: {format_proxy}] [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
            open("logs.txt", "a").write(f"\nV2 [PROXY: {format_proxy}] [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
            self.total_errors += 1
            self._total_errors += 1
        finally:
            await asyncio.sleep(0.1)