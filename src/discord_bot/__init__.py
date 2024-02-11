import discord, time, json
from discord import Option

async def start(self):
    bot = discord.Bot()
    
    @bot.event
    async def on_ready():
        open("logs.txt", "a").write(f"\nMAIN THREAD [{time.strftime('%H:%M:%S', time.localtime())}] started discord bot")
    
    @bot.command(description="Add a new user that has permission to use the bot")
    async def add_authorized_user(ctx, user: Option(discord.Member, description="user to give permission to")):
        if ctx.author.id not in self.discord_bot["authorized_users"]:
            return await ctx.respond(f"You are not authorized to do this", ephemeral=True)
        elif user.id == ctx.author.id:
            return await ctx.respond(f"You can't add yourself to the list", ephemeral=True)
        elif user.bot:
            return await ctx.respond(f"You can't add a discord bot to the list", ephemeral=True)
        elif user.id in self.discord_bot["authorized_users"]:
            return await ctx.respond(f"User <@{user.id}> is already authorized", ephemeral=True)
        else:
            data = json.loads(open("config.json", "r").read())
            data["discord_bot"]["authorized_users"].append(user.id)
            open("config.json", "w").write(json.dumps(data, indent=4))
            return await ctx.respond(f"Added user <@{user.id}> into whitelist")
    
    @bot.command(description="return stats of the sniper")
    async def stats(ctx):
        if ctx.author.id not in self.discord_bot["authorized_users"]:
            return await ctx.respond(f"You are not authorized to do this", ephemeral=True)
        stats = "Total Searches: " + repr(self.total_searchers) + "\n\nRun time: " + self.format_duration(time.time() - self.start_time) + "\n\n\nSearch Logs:\n" + '\n'.join(log for log in self.search_logs) + f"\n\nBuy Logs:" + '\n'.join(log for log in self.buy_logs) + f"\n\n\nTotal Items bought: {len(self.buy_logs)}" + "\n\n\nError Logs:\n" + '\n'.join(log for log in self.error_logs)
        return await ctx.respond(stats)
    
    @bot.command(description="add new item id")
    async def add_item(ctx, item_id: Option(int, description="item id"), price: Option(int, description="price to buy at")):
        if ctx.author.id not in self.discord_bot["authorized_users"]:
            return await ctx.respond(f"You are not authorized to do this", ephemeral=True)
        elif str(item_id) in self.items["list"] and self.items["list"][str(item_id)]["max_price"] == price:
            return await ctx.respond(f"Item already in list and has the same max price", ephemeral=True)
        self.items["list"][str(item_id)] = {"max_price": price}
        data = json.loads(open("config.json", "r").read())
        data["items"]["list"][str(item_id)] = {"max_price": price}
        open("config.json", "w").write(json.dumps(data, indent=4))
        return await ctx.respond(f"Successfully added item id `{item_id}` for the price of `{price}`")
    
    @bot.command(description="Remove item id")
    async def remove_item(ctx, item_id: Option(int, description="item id you want to remove")):
        if ctx.author.id not in self.discord_bot["authorized_users"]:
            return await ctx.respond(f"You are not authorized to do this", ephemeral=True)
        elif str(item_id) not in self.items["list"]:
            return await ctx.respond(f"Item id not in list", ephemeral=True)
        
        del self.items["list"][str(item_id)]
        data = json.loads(open("config.json", "r").read())
        del data["items"]["list"][str(item_id)]
        open("config.json", "w").write(json.dumps(data, indent=4))
        return await ctx.respond(f"Removed item id `{item_id}`")

    @bot.command(description="change max price")
    async def remove_item(ctx, item_id: Option(int, description="item id you want to remove")):
        if ctx.author.id not in self.discord_bot["authorized_users"]:
            return await ctx.respond(f"You are not authorized to do this", ephemeral=True)
        elif str(item_id) not in self.items["list"]:
            return await ctx.respond(f"Item id not in list", ephemeral=True)
        
        del self.items["list"][str(item_id)]
        data = json.loads(open("config.json", "r").read())
        del data["items"]["list"][str(item_id)]
        open("config.json", "w").write(json.dumps(data, indent=4))
        return await ctx.respond(f"Removed item id `{item_id}`")
        
    @bot.event
    async def on_application_command_error(ctx, error):
        return await ctx.respond(f"An error occurred: {error}", ephemeral=True)
            
    await bot.start(self.discord_bot["token"])