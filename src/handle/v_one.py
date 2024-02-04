import time, os, aiohttp, asyncio

from . import split_list

from ..lookup import v_one
from ..lookup import reseller
from ..buy import buy
from concurrent.futures import CancelledError

async def run(self):
    open("logs.txt", "a").write(f"\nV1 [{time.strftime('%H:%M:%S', time.localtime())}] has started up")
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})
    
    items = split_list.get([*self.items["list"].keys()])
    while True:
     try:
        for index, item_list in enumerate(items):
            if index > 0:
                print_data(self)
                try:
                    await asyncio.sleep(max((60 / self.searches_a_minute["v_one"]) - max(sum(list(self.average_speed_v1)) / len(self.average_speed_v1), 0), 0))
                except:
                    await asyncio.sleep(1)
            item_data = await v_one.get(self, item_list, session)
            self.total_searchers += len(item_list)
            self._total_searchers += len(item_list)
            for item in item_data:
                if not item.get("itemRestrictions"):
                    if str(item.get("id")) in self.items["list"]:
                        del self.items["list"][str(item.get("id"))]
                    continue
                if 'Collectible' in item.get("itemRestrictions"):
                    info = {"price": int(item.get("lowestResalePrice", 999999999)), "productid_data": None, "collectible_item_id": item.get("collectibleItemId"), "item_id": str(item.get("id"))}
                    
                    if item.get("priceStatus") == "Off Sale":
                        if str(item.get("id")) in self.items["list"]:
                            del self.items["list"][str(item.get("id"))]
                        continue
                    
                    if not info["collectible_item_id"] in self.limited_collectible_ids and not info["collectible_item_id"] in self.all_limited_collectible_ids:
                        self.limited_collectible_ids.append(info["collectible_item_id"])
                        self.all_limited_collectible_ids[info["collectible_item_id"]] = info["item_id"]
                        
                    if not item.get("hasResellers") or info['item_id'] in self.items["list"] and info['price'] > self.items["list"][info['item_id']]["max_price"]:
                        continue
            
                    rss = await reseller.get(self, info["collectible_item_id"], session)
                    info['price'] = rss['price']
                    info["productid_data"] = rss["collectibleProductId"]
                    info["collectible_item_instance_id"] = rss["collectibleItemInstanceId"]
                    if info['item_id'] in self.items["list"]:
                        if info['price'] > self.items["list"][info['item_id']]["max_price"]:
                            continue
                        await buy.purchase(self, info, session)
                elif 'Limited' in item.get("itemRestrictions") or 'LimitedUnique' in item.get("itemRestrictions"):
                    if not item.get("hasResellers") or item.get("lowestResalePrice") > self.items["list"][str(item.get("id"))]["max_price"]:
                        continue
                    await buy.purchase_limited(self, {"expectedCurrency": 1,"expectedPrice": item.get("lowestResalePrice"), "expectedSellerId": 1}, item.get("id"), item.get("productId"), session)
                else:
                    if str(item.get("id")) in self.items["list"]:
                        del self.items["list"][str(item.get("id"))]
                    continue
                
     except Exception as e:
        await session.close()
        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})  # just to refresh the session
        self.error_logs.append(f"V1 [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
        open("logs.txt", "a").write(f"\nV1 [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
        self.total_errors += 1
        self._total_errors += 1
        
     finally:   
        items = split_list.get([*self.items["list"].keys()])
        
        print_data(self)
        if self.restart_after_config["total_errors"] > 0 and self.restart_after_config["total_errors"] <= self._total_errors or self.restart_after_config["total_buys"] > 0 and self.restart_after_config["total_buys"] <= self._total_buys or self.restart_after_config["seconds"] > 0 and self.restart_after_config["seconds"] <= int((time.time() - self._start_time) % 60) or self.restart_after_config["total_searchers"] > 0 and self.restart_after_config["total_searchers"] <= self._total_searchers:
            await session.close()
            await self.RESTART.COMMAND.IGNORE.THIS
            
        try:
            await asyncio.sleep(max((60 / self.searches_a_minute["v_one"]) - max(sum(list(self.average_speed_v1)) / len(self.average_speed_v1), 0), 0))
        except:
            await asyncio.sleep(1)
        
def print_data(self):
        os.system(self.clear)
        print("Total Searches: " + repr(self.total_searchers)
              + "\n\nRun time: " + self.format_duration(time.time() - self.start_time)
              + "\n\n\nSearch Logs:\n" + '\n'.join(log for log in self.search_logs) 
              + f"\n\nBuy Logs:" + '\n'.join(log for log in self.buy_logs) 
              + f"\n\n\nTotal Items bought: {len(self.buy_logs)}" 
              + "\n\n\nError Logs:\n" + '\n'.join(log for log in self.error_logs)
        )