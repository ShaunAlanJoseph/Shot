import os
import discord
from discord.ext import commands
from discord import app_commands
import custom_discord_functions as cdf
import custom_string_functions as csf
import config_reader as cr
from Data import emojis
import asyncio

DISCORD_API_SECRET = os.environ['DISCORD_API_SECRET']
BOT_CONFIG_FILE = "bot.config"

bot_admin_users = cr.config_reader(BOT_CONFIG_FILE, "bot_admin_users")
bot_admin_users = bot_admin_users.split(",") if bot_admin_users else []
bot_admin_users = [int(x) for x in bot_admin_users]
bot_admin_roles = cr.config_reader(BOT_CONFIG_FILE, "bot_admin_roles")
bot_admin_roles = bot_admin_roles.split(",") if bot_admin_roles else []
bot_admin_roles = [int(x) for x in bot_admin_roles]

def is_bot_admin():
  async def predicate(ctx):
    if cdf.check_has_role(ctx.author, bot_admin_roles) or cdf.check_user_in_list(ctx.author, bot_admin_users):
        return True
    await ctx.reply(f"What makes you think that you can run this command?? {emojis.sneezing_face}")
    return False
  return commands.check(predicate)

async def run():
  intents = discord.Intents.default()
  intents.message_content = True
  
  bot_msg_channel = ""
  
  bot = commands.Bot(command_prefix="!", intents=intents)
  
  await bot.load_extension("daily_questions_cog")

  def config(key, group = "", section = ""):
    return cr.config_reader(BOT_CONFIG_FILE, key, group, section)
  
  @bot.event
  async def on_ready():
    print(f"Logged in as User: {bot.user} (ID: {bot.user.id})")
    print("------")
    await bot.tree.sync()
    nonlocal bot_msg_channel
    bot_msg_channel = int(config("bot_msg_channel"))
    bot_msg_channel = bot.get_channel(bot_msg_channel)
    
    await bot_msg_channel.send(f"Hi, I've logged in as **User:** {bot.user} (**ID:** {bot.user.id})")
  
  async def update_presence():
    member_count = 0
    for guild in bot.guilds:
      if guild.member_count:
        member_count += guild.member_count
    activity = discord.Activity(name=f"{member_count} skill issues.", type=discord.ActivityType.listening)
    bot.change_presence(activity=activity)
  
  @bot.event
  async def on_member_join(member: discord.Member):
    await update_presence()
  
  @bot.hybrid_command()
  @is_bot_admin()
  async def ping(ctx):
    await ctx.send(f"{ctx.author.mention} pong!")
    await ctx.author.send("I see that you ran a command.")
  
  @bot.command(name="dq.reload")
  @is_bot_admin()
  async def daily_question_reload(ctx):
    try:
      await bot.reload_extension("daily_questions_cog")
      await ctx.send(f"DailyQuestions_Cog has been reloaded successfully.")
      print(f"DailyQuestions_Cog reloaded successfully.")
    except:
      await ctx.send(f"Failed to reload DailyQuestions_Cog. Error: {Exception}")
      print(f"Failed to reload DailyQuestions_Cog. Error: {Exception}")
  
  await bot.start(DISCORD_API_SECRET)

if __name__ == "__main__":
  asyncio.run(run())