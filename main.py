import os
import discord
import custom_string_functions as csf
from datetime import datetime, timedelta
from discord.ext import commands
from discord.ext import tasks
import daily_questions as dq

DISCORD_API_SECRET = os.environ['DISCORD_API_SECRET']


def run():
  intents = discord.Intents.default()
  intents.message_content = True

  bot = commands.Bot(command_prefix="!", intents=intents)

  @bot.event
  async def on_ready():
    print(f'Logged in as User: {bot.user} (ID: {bot.user.id})')
    print('------')
    check_dq_time.start()

  @bot.command()
  async def ping(ctx):
    await ctx.send(f"{ctx.author.mention} pong!")

  @bot.command()
  async def daily_ques(ctx, date):
    await ctx.message.delete()
    date = dq.str_to_datetime(date)
    if not date:
      await ctx.send("Invalid date format!")
      return
    await dq.get_print_questions(ctx, date)

  @bot.command()
  async def daily_ques_set_time(ctx, time):
    await ctx.message.delete()
    hour = csf.str_before(time, ":")
    min = csf.str_after(time, ":")
    try:
      time = datetime(1, 1, 1, int(hour), int(min))
    except:
      await ctx.send("Invalid time format!")
      return
    dq.set_time(time)
    await ctx.send(f"Time set to {time.strftime('%H:%M')}")

  @bot.command()
  async def daily_ques_set_channel(ctx, channel):
    await ctx.message.delete()
    if bot.get_channel(int(channel)):
      dq.set_channel(channel)
      await ctx.send(f"Channel set to {channel}")
    else:
      await ctx.send("Invalid channel!")

  @tasks.loop(seconds=45)
  async def check_dq_time():
    time = dq.get_time()
    now = datetime.now()
    now += timedelta(hours=5, minutes=30)
    print(time, now.strftime("%H:%M"))
    if (time != now.strftime("%H:%M")):
      return

    channel = dq.get_channel_id()
    channel = bot.get_channel(int(channel))
    await channel.send("Now is the time!!")
    await dq.get_print_questions(channel, now)

  bot.run(DISCORD_API_SECRET)

if __name__ == "__main__":
  run()
