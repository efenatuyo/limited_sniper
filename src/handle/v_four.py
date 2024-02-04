import time, aiohttp, asyncio

from ..buy import buy
from ..lookup import v_four
from ..lookup import reseller

async def run(self):
    open("logs.txt", "a").write(f"\nV4 [{time.strftime('%H:%M:%S', time.localtime())}] has started up")
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})
    while True:
        try:
            for index, item_id in enumerate(self.items["list"].copy()):
                if index > 0:
                    try:
                        await asyncio.sleep(max((60 / self.searches_a_minute["v_four"]) - max(sum(list(self.average_speed_v4)) / len(self.average_speed_v4), 0), 0))
                    except:
                        await asyncio.sleep(1)
                item = await v_four.get(self, item_id, session)
                self.total_searchers += 1
                self._total_searchers += 1
                if not item.get("itemRestrictions"):
                    if str(item.get("id")) in self.items["list"]:
                        del self.items["list"][str(item.get("id"))]
                    continue                
                if 'Collectible' in item.get("itemRestrictions"):
                    info = {"price": int(item.get("lowestResalePrice", 999999999)), "productid_data": None, "collectible_item_id": item.get("collectibleItemId"), "item_id": str(item.get("id"))}
                    if item.get("priceStatus") == "Off Sale":
                        if info['item_id'] in self.items["list"]:
                            del self.items["list"][info['item_id']]
                        continue
                    if not info["collectible_item_id"] in self.limited_collectible_ids and not info["collectible_item_id"] in self.all_limited_collectible_ids:
                        self.limited_collectible_ids.append(info["collectible_item_id"])
                        self.all_limited_collectible_ids[info["collectible_item_id"]] = info["item_id"]
                        
                    if not item.get("hasResellers") or info['price'] > self.items["list"][info['item_id']]["max_price"]:
                        continue
            
                    rss = await reseller.get(self, info["collectible_item_id"], session)
                    info['price'] = rss['price']
                    info["productid_data"] = rss["collectibleProductId"]
                    info["collectible_item_instance_id"] = rss["collectibleItemInstanceId"]
            
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
        except asyncio.exceptions.CancelledError:
            await session.close()
            return
        except Exception as e:
            await session.close()
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), cookies={".ROBLOSECURITY": self.cookie}, headers={'Accept-Encoding': 'gzip, deflate'})  # just to refresh the session
            self.error_logs.append(f"V4 [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
            open("logs.txt", "a").write(f"\nV4 [{time.strftime('%H:%M:%S', time.localtime())}] {e}")
            self.total_errors += 1
            self._total_errors += 1
        finally:
            try:
                await asyncio.sleep(max((60 / self.searches_a_minute["v_four"]) - max(sum(list(self.average_speed_v4)) / len(self.average_speed_v4), 0), 0))
            except:
                await asyncio.sleep(1)