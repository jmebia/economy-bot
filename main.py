import string
from tokenize import String
import discord
import random
import json
import pathlib
import os
from datetime import datetime, timedelta
from discord.ext import commands

# gets the current directory of the working script
current_dir = str(pathlib.Path(__file__).parent.resolve())
os.chdir(current_dir)

client = commands.Bot(command_prefix = "ag? ")

account_template = {
    "wallet" : 0,
    "next_daily": 0,
    "inventory" : []
}


@client.event
async def on_ready():
    print("Ready")

@client.command()
async def balance(ctx):
    a = await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    wallet_amount = users[str(user.id)]["wallet"]

    em = discord.Embed(title = f"{ctx.author.name}'s balance", color = discord.Color.red())
    em.add_field(name = "Wallet", value = wallet_amount)
    await ctx.reply(f"Here are your balances" ,embed = em)

@client.command()
async def daily(ctx):
    a = await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    earnings = 10

    # current date and time
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    print("timestamp =", timestamp)
    next_daily = users[str(user.id)]["next_daily"]

    print("next daily =", next_daily)

    if timestamp > next_daily:
        em = discord.Embed(title = f"{ctx.author.name}'s Daily Check-in", color = discord.Color.red())
        em.add_field(name = "Rewards received", value = f"{earnings} coins")
        await ctx.reply(f"Here's your daily reward! Your next claim will be after 20 hours.", embed = em)

        # current date and time
        new_daily = datetime.now() + timedelta(hours=20)
        users[str(user.id)]["next_daily"] = datetime.timestamp(new_daily)

        users[str(user.id)]["wallet"] += earnings
        with open("accounts.json", "w") as f:
            json.dump(users, f)
    else:
        next = datetime.fromtimestamp(next_daily)
        date = next.strftime("%Y %B %d")
        time = next.strftime("%H:%M:%S")

        em = discord.Embed(title = f"{ctx.author.name}'s Daily Check-in", color = discord.Color.red())
        em.add_field(name = "Next claim on", value = f"{date} at {time}")
        await ctx.reply(f"Your next daily rewards are not yet ready!", embed = em)

@client.command()
async def send(ctx, member: discord.Member, value: int):
    # Send money from member A to member B. 
    # Member A loses amount value and Member B gains amount value

    a = await open_account(member)
    sender = ctx.author
    receiver = member
    users = await get_bank_data()
    earnings = value

    if not receiver.bot:
        if sender == receiver:
            await ctx.reply(f"You can't send to yourself!")
        elif users[str(sender.id)]["wallet"] < value:
            await ctx.reply(f"You don't have enough coins!")
        else:
            users[str(sender.id)]["wallet"] -= earnings
            users[str(receiver.id)]["wallet"] += earnings
            await ctx.send(f"{member.mention}, you just received received {earnings} coins from {sender.mention}!")
 
            with open("accounts.json", "w") as f:
                json.dump(users, f)
    else:
        await ctx.send(f"{sender.mention}, you can't send to a BOT!")

@client.command()
async def buyitem(ctx, id):
    items = await get_shop_data()

    if id in items:
        users = await get_bank_data()
        item = items[str(id)]
        price = item["value"]
        buyer = ctx.author
        a = await open_account(buyer)


        print("price: " + str(price))
        print("Buyer: " + str(buyer.id))
        if price > users[str(buyer.id)]["wallet"]:
            users[str(buyer.id)]["wallet"] -= price
            users[str(buyer.id)]["inventory"].append(id)
        else:
            await ctx.reply(f"Your coins isn't enough for this purchase.")
    else:
        await ctx.reply(f"The item you want to buy doesn't exist!")


@client.command()
async def itemshop(ctx):
    items = await get_shop_data()
    em = discord.Embed(title = f"Item Shop", color = discord.Color.red())
    print(items)
    for item in items:
        em.add_field(name = items[item]["name"] + " [ID: " + item + "]", value = items[item]["description"] + " [Price: " + str(items[item]["value"]) + " coins]")

    await ctx.send(f"Here's what we have.", embed = em)


#### HELPER FUNCTIONS

async def open_account(user):
    users = await get_bank_data()
    
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = account_template

    with open("accounts.json", "w") as f:
        json.dump(users, f)
    
    return True


async def get_bank_data():
    with open("accounts.json", "r") as f:
        users = json.load(f)
    return users

async def get_shop_data():
    with open("shop.json", "r") as f:
        items = json.load(f)
    return items


client.run('MzU0NDIxMjIzMDA4MjM5NjE3.Wa3ufA.K-LQpLr95Et6lJtDjLghW8cWP3Y')