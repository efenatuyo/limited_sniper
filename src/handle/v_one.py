import time, os, aiohttp, asyncio

from . import split_list

from ..lookup import v_one
from ..lookup import reseller
from ..buy import buy

async def run(self):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})
    
    items = split_list.get([*self.items["list"].keys()])
    while True:
     try:
        for index, item_list in enumerate(items):
            if index > 0:
                print_data(self)
                await asyncio.sleep(self.sleep_config["v2_searcher_sleep_in_s"])
            item_data = await v_one.get(self, item_list, session)
            self.total_searchers += len(item_list)
            for item in item_data:
                if 'Limited' not in item.get("itemRestrictions"):
                    info = {"price": int(item.get("lowestResalePrice", 999999999)), "productid_data": None, "collectible_item_id": item.get("collectibleItemId"), "item_id": str(item.get("id"))}
                    
                    if item.get("priceStatus") == "Off Sale":
                        del self.items["list"][info['item_id']]
                        continue
                    
                    if not info["collectible_item_id"] in self.limited_collectible_ids and not info["collectible_item_id"] in self.all_limited_collectible_ids:
                        self.limited_collectible_ids.append(info["collectible_item_id"])
                        self.all_limited_collectible_ids.append(info["collectible_item_id"])
                        
                    if not item.get("hasResellers") or info['price'] > self.items["list"][info['item_id']]["max_price"]:
                        continue
            
                    rss = await reseller.get(self, info["collectible_item_id"], session)
                    info['price'] = rss['price']
                    info["productid_data"] = rss["collectibleProductId"]
                    info["collectible_item_instance_id"] = rss["collectibleItemInstanceId"]
            
                    if info['price'] > self.items["list"][info['item_id']]["max_price"]:
                        continue
               
                    await buy.purchase(self, info, session)
                else:
                    if not item.get("hasResellers") or item.get("lowestResalePrice") > self.items["list"][str(item.get("id"))]["max_price"]:
                        continue
                    await buy.purchase_limited(self, {"expectedCurrency": 1,"expectedPrice": item.get("lowestResalePrice"), "expectedSellerId": 1}, item.get("id"), item.get("productId"), session)

     except Exception as e:
        await session.close()
        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})  # just to refresh the session
        self.error_logs.append(f"V1 [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
        
     finally:   
        items = split_list.get([*self.items["list"].keys()])
        
        print_data(self)
        await asyncio.sleep(self.sleep_config["v2_searcher_sleep_in_s"])
        
def print_data(self):
        os.system(self.clear)
        print("Total Searches: " + repr(self.total_searchers)
              + "\n\nRun time: " + self.format_duration(time.time() - self.start_time)
              + "\n\n\nSearch Logs:\n" + '\n'.join(log for log in self.search_logs) 
              + f"\n\nBuy Logs:" + '\n'.join(log for log in self.buy_logs) 
              + f"\n\n\nTotal Items bought: {len(self.buy_logs)}" 
              + "\n\n\nError Logs:\n" + '\n'.join(log for log in self.error_logs)
        )