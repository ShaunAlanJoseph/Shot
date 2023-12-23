import os
import discord
from discord.ext import commands
import config_reader as cr

DISCORD_API_SECRET = os.environ['DISCORD_API_SECRET']
BOT_CONFIG_FILE = "bot.config"

def run():
  intents = discord.Intents.default()
  intents.message_content = True
  
  bot_message_channel = ""
  
  bot = commands.Bot(command_prefix="!", intents=intents)
  
  @bot.event
  async def on_ready():
    print(f"Logged in as User: {bot.user} (ID: {bot.user.id})")
    print("------")
    
    nonlocal bot_message_channel
    bot_msg_channel = int(config("bot_msg_channel"))
    bot_msg_channel = bot.get_channel(bot_msg_channel)
    
    bot_msg_channel.send(f"Hi, I've logged in as User: {bot.user} (ID: {bot.user.id})")
  
  @bot.command()
  async def ping(ctx):
    await ctx.send(f"{ctx.author.mention} pong!")
    await ctx.author.send("I see that you ran a command.")
  
  bot.load_extension("daily_questions_cog")
  
  bot.run(DISCORD_API_SECRET)
    

if __name__ == "__main__":
  run()

def config(key, group = "", section = ""):
  return cr.config_reader(BOT_CONFIG_FILE, key, group, section)