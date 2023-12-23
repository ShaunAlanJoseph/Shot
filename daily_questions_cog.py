from discord.ext import commands, tasks
import custom_string_functions as csf
import daily_questions as dq
from datetime import datetime, timedelta
import config_reader as cr
from Data import emojis

class DailyQuestions_Cog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.check_dq_time.start()
  
  @commands.command(name="dq.add")
  async def dq_add(self, ctx):
    msg = ctx.message.content
    msg = csf.str_after(msg, "```")
    msg = csf.str_before(msg, "```")
    dqf = dq.DailyQuestions_File()
    new_day = dq.DailyQuestions_Day(msg)
    if dqf.write_new_day(new_day):
      await ctx.send(f"Questions for ({new_day.nth}) {new_day.strftime('%d-%m-%Y')} have been added.")
    else:
      await ctx.send(f"({new_day.nth}) {new_day.strftime('%d-%m-%Y')} -> Clashes with an existing day.")
  
  @commands.command(name="dq.remove")
  async def dq_remove(self, ctx, day):
    if not day.isdigit():
      day = dq.str_to_datetime(day)
      if not day:
        await ctx.send("Invalid date!")
    
    dqf = dq.DailyQuestions_File()
    daily_questions = dqf.get_questions()
    removed_day = dqf.remove_day(daily_questions[day])
    if removed_day:
      await ctx.send(f"Questions for ({removed_day.nth}) {removed_day.strftime('%d-%m-%Y')} have been removed.")
    else:
      if isinstance(day, datetime):
        await ctx.send(f"Questions for {day.strftime('%d-%m-%Y')} were not found.")
      else:
        await ctx.send(f"Questions for Day {day} were not found.")
  
  @commands.command(name="dq.list_days")
  async def dq_list_days(self, ctx):
    dqf = dq.DailyQuestions_File()
    day_list = dqf.get_day_list()
    msg = ""
    for x in day_list:
      msg += x[0] + " -> " + x[1].strftime('%d-%m-%Y') + "\n"
    await ctx.send(f"Here is a list of days:\n{msg}")
  
  @commands.command(name="dq.get_day_raw")
  async def dq_get_day_raw(self, ctx, day):
    if not day.isdigit():
      day = dq.str_to_datetime(day)
      if not day:
        await ctx.send("Invalid date!")
        return
    else:
      day = int(day)
    
    dqf = dq.DailyQuestions_File()
    daily_questions = dqf.get_questions()
    if day in daily_questions:
      day = daily_questions[day]
      msg = dq.day.to_str()
      await ctx.send(f"Questions for ({day.nth}) {day.date.strftime('%d-%m-%Y')}:\n```\n{msg}\n```")
    else:
      if isinstance(day, int):
        await ctx.send(f"Questions for Day {day} were not found.")
      else:
        await ctx.send(f"Questions for {day.strftime('%d-%m-%Y')} were not found.")
  
  @commands.command(name="dq.get_day")
  async def dq_get_day(self, ctx, day):
    if not day.isdigit():
      day = dq.str_to_datetime(day)
      if not day:
        await ctx.send("Invalid date!")
        return
    else:
      day = int(day)
    
    dqf = dq.DailyQuestions_File()
    day = dqf.day_exists(day)
    if day:
      msg = dq.day.to_str()
      await ctx.send(f"Questions for ({day.nth}) {day.date.strftime('%d-%m-%Y')}:\n```\n{msg}\n```")
    else:
      if isinstance(day, int):
        await ctx.send(f"Questions for Day {day} were not found.")
      else:
        await ctx.send(f"Questions for {day.strftime('%d-%m-%Y')} were not found.")
    pass
  
  @commands.command(name="dq.set_time")
  async def dq_set_time(self, ctx, time):
    hours = int(csf.str_before(time, ":"))
    mins = int(csf.str_after(time, ":"))
    try:
      datetime(0, 0, 0, hours, mins)
    except:
      await ctx.send("Invalid time!")
      return
    dqf = dq.DailyQuestions_File()
    dqf.details.time = time
    dqf.write_details()
  
  @commands.command(name="dq.get_time")
  async def dq_get_time(self, ctx):
    dqf = dq.DailyQuestions_File()
    await ctx.send(f"The time for daily questions is {dqf.details.time}.")
    pass
  
  @commands.command(name="dq.set_ques_chnl")
  async def dq_set_ques_chnl(self, ctx, channel: int):
    channel = self.bot.get_channel(channel)
    if not channel:
      await ctx.send("Invalid channel!")
      return
    dqf = dq.DailyQuestions_File()
    dqf.details.ques_channel = channel
    dqf.write_details()
  
  @commands.command(name="dq.get_ques_chnl")
  async def dq_get_ques_chnl(self, ctx):
    dqf = dq.DailyQuestions_File()
    channel = self.bot.get_channel(dqf.details.ques_channel)
    await ctx.send(f"The channel for daily questions is {channel.category}: {channel.name} - {channel.id}.")
  
  @commands.command(name="dq.set_soln_chnl")
  async def dq_set_soln_chnl(self, ctx, channel: int):
    channel = self.bot.get_channel(channel)
    if not channel:
      await ctx.send("Invalid channel!")
      return
    dqf = dq.DailyQuestions_File()
    dqf.details.soln_channel = channel
    dqf.write_details()
  
  @commands.command(name="dq.get_soln_chnl")
  async def dq_get_soln_chnl(self, ctx):
    dqf = dq.DailyQuestions_File()
    channel = self.bot.get_channel(dqf.details.soln_channel)
    await ctx.send(f"The channel for the solutions is {channel.category}: {channel.name} - {channel.id}.")
  
  @commands.command(name="dq.set_announcement_chnl")
  async def dq_set_announcement_chnl(self, ctx, channel: int):
    channel = self.bot.get_channel(channel)
    if not channel:
      await ctx.send("Invalid channel!")
      return
    dqf = dq.DailyQuestions_File()
    dqf.details.announcement_channel = channel
    dqf.write_details()
  
  @commands.command(name="dq.get_announcement_chnl")
  async def dq_get_announcement_chnl(self, ctx):
    dqf = dq.DailyQuestions_File()
    channel = self.bot.get_channel(dqf.details.announcement_channel)
    await ctx.send(f"The channel for daily question announcements is {channel.category}: {channel.name} - {channel.id}.")
  
  @commands.command(name="dq.set_admin_roles")
  async def dq_set_admin_roles(self, ctx, admin_roles):
    admin_roles = admin_roles[1 : len(admin_roles) - 1]
    admin_roles = admin_roles.split(",")
    for x in range(len(admin_roles)):
      admin_roles[x] = int(admin_roles[x])
      user = ctx.guild.get_role(admin_roles[x])
      possible = True
      if not user:
        await ctx.send(f"{admin_roles[x]} is not a valid user.")
        possible = False
      if not possible:
        return
    dqf = dq.DailyQuestions_File()
    dqf.details.admin_roles = admin_roles
    dqf.write_details()
  
  @commands.command(name="dq.get_admin_roles")
  async def dq_get_admin_roles(self, ctx):
    dqf = dq.DailyQuestions_File()
    admin_roles_str = "["
    for x in dqf.details.admin_roles:
      admin_roles += x + ","
    admin_roles_str = admin_roles_str[0 : len(admin_roles_str) - 1] + "]"
    await ctx.send(f"The daily question admins are:\n{admin_roles_str}")
  
  @commands.command(name="dq.set_admin_users")
  async def dq_set_admin_users(self, ctx, admin_users):
    admin_users = admin_users[1 : len(admin_users) - 1]
    admin_users = admin_users.split(",")
    for x in range(len(admin_users)):
      admin_users[x] = int(admin_users[x])
      user = self.bot.get_user(admin_users[x])
      possible = True
      if not user:
        await ctx.send(f"{admin_users[x]} is not a valid user.")
        possible = False
      if not possible:
        return
    dqf = dq.DailyQuestions_File()
    dqf.details.admin_users = admin_users
    dqf.write_details()
  
  @commands.command(name="dq.get_admin_users")
  async def dq_get_admin_users(self, ctx):
    dqf = dq.DailyQuestions_File()
    admin_users_str = "["
    for x in dqf.details.admin_users:
      admin_users += x + ","
    admin_users_str = admin_users_str[0 : len(admin_users_str) - 1] + "]"
    await ctx.send(f"The daily question admins are:\n{admin_users_str}")
  
  @tasks.loop(seconds=45)
  async def check_dq_time(self):
    dq_time = dq.get_dq_time()
    curr_time = datetime.now() + timedelta(hours=5, minutes=30)
    if dq_time.strftime('%H:%M') == curr_time.strftime('%H:%M'):
      print(f"dq: {dq_time.strftime('%H:%M')} now: {curr_time.strftime('%H:%M')} Now is the time!")
      announce_questions_and_soln(self.bot)
    else:
      print(f"dq: {dq_time.strftime('%H:%M')} now: {curr_time.strftime('%H:%M')}")
  
  @check_dq_time.before_loop
  async def before_check_dq_time(self):
    await self.bot.wait_until_ready()

def setup(bot):
  bot.add_cog(DailyQuestions_Cog(bot))

async def announce_questions_and_soln(bot):
  date = datetime.now().strftime('%d-%m-%Y')
  date = dq.str_to_datetime(date)
  dqf = dq.DailyQuestions_File()
  ques_msg = dqf.days[date].to_announce_ques()
  soln_msg = dqf.days[date].nth - 1
  if soln_msg:
    soln_msg = dqf.days[soln_msg].to_announce_soln()
    soln_channel = dqf.details.soln_channel
    soln_channel = bot.get_channel(soln_channel)
    await soln_channel.send(soln_msg["title"])
    for x in soln_msg["questions"]:
      await soln_channel.send(x)
  ques_channel = dqf.details.ques_channel
  ques_channel = bot.get_channel(ques_channel)
  await ques_channel.send(ques_msg["title"])
  for x in ques_msg["questions"]:
    msg = await ques_channel.send(x)
    msg.add_reaction(emojis.white_check_mark)
    