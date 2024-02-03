import uuid, time

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