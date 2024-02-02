import time, aiohttp, asyncio

from ..buy import buy
from ..lookup import v_four
from ..lookup import reseller

async def run(self):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})
    while True:
        try:
            for index, item_id in enumerate(self.items["list"].copy()):
                if index > 0:
                    await asyncio.sleep(self.sleep_config["v4_searcher_sleep_in_s"])
                item = await v_four.get(self, item_id, session)
                self.total_searchers += 1
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
            self.error_logs.append(f"V4 [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
        finally:
            await asyncio.sleep(self.sleep_config["v4_searcher_sleep_in_s"])