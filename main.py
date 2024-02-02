import src, asyncio, json

asyncio.run(src.sniper(json.loads(open("config.json", "r").read())).run())