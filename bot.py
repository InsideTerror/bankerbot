#!/usr/bin/env python3
"""
BankerBot — Global Economy Bridge
Main entry point that loads all cogs and runs the bot.
"""

import os
import discord
from discord.ext import commands

# ===================== BOT CONFIG =====================
DISCORD_BOT_TOKEN = "REPLACE_WITH_REAL_TOKEN"
# ======================================================

# Enable required intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True  # Required if using on_message or text-based logic
#Version 1.2 : Fixed loading order, added error handling for cog loading

# Create bot instance
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands successfully.")
    except Exception as e:
        print(f"⚠️ Slash command sync failed: {e}")


# ✅ Correct async cog loader
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"🔹 Loaded cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")


async def main():
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    import asyncio
    if DISCORD_BOT_TOKEN.startswith("PUT_"):
        print("❌ Please set your bot token in main.py.")
    else:
        asyncio.run(main())
