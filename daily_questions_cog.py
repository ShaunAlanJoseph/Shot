from discord.ext import commands, tasks
import custom_string_functions as csf
import custom_random_functions as crf
import custom_discord_functions as cdf
import daily_questions as DQ
from datetime import datetime, timedelta
from Data import emojis

dq_admin_users = set()
dq_admin_roles = set()
dq_time = ""

dq_questions_posted_file = "/home/runner/Shot/Data/Daily Questions/questions_posted.data"

def is_dq_admin():
  async def predicate(ctx):
    if cdf.check_has_role(ctx.author, dq_admin_roles) or cdf.check_user_in_list(ctx.author, dq_admin_users):
        return True
    await ctx.reply(f"Imagine not having the perms to run that command. {emojis.sneezing_face}")
    return False
  return commands.check(predicate)

class DailyQuestions_Cog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    dq_details = DQ.DailyQuestions_DayDetails()
    global dq_admin_users, dq_admin_roles, dq_time
    for x in dq_details.admin_users:
      dq_admin_users.add(x)
    for x in dq_details.admin_roles:
      dq_admin_roles.add(x)
    dq_time = dq_details.time
    self.check_dq_time.start()
  
  @commands.command(name="dq.ping", description="Pongs you...duh!")
  @is_dq_admin()
  async def dq_ping(self, ctx):
    await ctx.send(f"{ctx.author.mention} pong!!")
  
  @commands.command(name="dq.add")
  @is_dq_admin()
  async def dq_add(self, ctx):
    msg = ctx.message.content
    msg = csf.after(msg, "```")
    msg = csf.before(msg, "```")
    dq = DQ.DailyQuestions()
    try:
      new_day = dq.add_day(msg)
      await ctx.reply(f"Questions for ({new_day.nth}) {new_day.start_date.strftime('%Y-%m-%d')} have been added.")
    except Exception as ex:
      print(ex)
      await ctx.reply(f"Error: {ex}")
  
  @commands.command(name="dq.remove")
  @is_dq_admin()
  async def dq_remove(self, ctx, day = ""):
    day = get_nth_or_date(day)
    if not day:
      await ctx.reply(f"Invalid Day!")
      return
    
    dq = DQ.DailyQuestions()
    try:
      removed_day = dq.remove_day(day)
      await ctx.reply(f"Removed day: ({removed_day['day'].nth}) {removed_day['day'].start_date.strftime('%Y-%m-%d')}.\n**Raw:**\n```\n{removed_day['raw']}\n```")
    except Exception as ex:
      print(ex)
      await ctx.reply(f"Error: {ex}")
  
  @commands.command(name="dq.replace")
  @is_dq_admin()
  async def dq_replace(self, ctx, old_day):
    old_day = get_nth_or_date(old_day)
    if not old_day:
      await ctx.reply(f"Invalid Day!")
      return
    
    dq = DQ.DailyQuestions()
    try:
      removed_day = dq.remove_day(old_day)
      await ctx.reply(f"Removed day: ({removed_day['day'].nth}) {removed_day['day'].start_date.strftime('%Y-%m-%d')}.\n**Raw:**\n```\n{removed_day['raw']}\n```")
    except Exception as ex:
      await ctx.reply(f"Error: {ex}")
    
    msg = ctx.message.content
    msg = csf.after(msg, "```")
    msg = csf.before(msg, "```")
    new_day = DQ.DailyQuestions_Day(msg)
    
    try:
      new_day = dq.add_day(msg)
      await ctx.reply(f"Questions for ({new_day.nth}) {new_day.start_date.strftime('%Y-%m-%d')} have been added.")
    except Exception as ex:
      print(ex)
      await ctx.reply(f"Error: {ex}")
  
  @commands.command(name="dq.list_days")
  @is_dq_admin()
  async def dq_list_days(self, ctx):
    dq = DQ.DailyQuestions()
    day_list = dq.get_day_list()
    msg = ""
    for i in range(1, len(day_list)):
      msg += f"{day_list[i]['nth']}) -> {day_list[i]['start_date'].strftime('%Y-%m-%d')} ({day_list[i]['duration']})\n"
    await ctx.reply(f"Here is a list of days:\n{msg}")
  
  @commands.command(name="dq.day_raw")
  @is_dq_admin()
  async def dq_day_raw(self, ctx, day):
    day = get_nth_or_date(day)
    if not day:
      await ctx.reply(f"Invalid Day!")
      return
    
    dq = DQ.DailyQuestions()
    try:
      curr_day_raw = dq.get_day_raw(day)
      await ctx.reply(f"```\n{curr_day_raw}\n```")
    except Exception as ex:
      print(ex)
      await ctx.reply(f"Error: {ex}")
  
  @commands.command(name="dq.announce_ques")
  @is_dq_admin()
  async def dq_announce_ques(self, ctx, date):
    day = get_nth_or_date(date)
    if not day:
      await ctx.reply(f"Invalid Day!")
      return
  
    dq = DQ.DailyQuestions()
    try:
      day = dq.get_day(day)
      dq_details = DQ.DailyQuestions_Details()
      await announce_ques(self.bot, day, dq_details.ques_chnl)
    except Exception as ex:
      print(ex)
      await ctx.reply(f"Error: {ex}")
  
  @commands.command(name="dq.announce_soln")
  @is_dq_admin()
  async def dq_announce_soln(self, ctx, date):
    day = get_nth_or_date(date)
    if not day:
      await ctx.reply(f"Invalid Day!")
      return
  
    dq = DQ.DailyQuestions()
    try:
      day = dq.get_day(day)
      dq_details = DQ.DailyQuestions_Details()
      await announce_soln(self.bot, day, dq_details.soln_chnl)
    except Exception as ex:
      print(ex)
      await ctx.reply(f"Error: {ex}")
  
  @commands.command(name="dq.day_format")
  @is_dq_admin()
  async def dq_day_format(self, ctx):
    day_format = """```
    <d_nth></d_nth>
    <d_date></d_date>
    <d_duration>1</d_duration>
    <d_note></d_note>
    <q>
    <q_n>1</q_n>
    <q_lvl></q_lvl>
    <q_pts></q_pts>
    <q_link></q_link>
    <q_note></q_note>
    <q_soln></q_soln>
    </q>
    <q>
    <q_n>2</q_n>
    <q_lvl></q_lvl>
    <q_pts></q_pts>
    <q_link></q_link>
    <q_note></q_note>
    <q_soln></q_soln>
    </q>
    ```"""
    await ctx.reply(f"{day_format}")
  
  @commands.command(name="dq.set_time")
  @is_dq_admin()
  async def dq_set_time(self, ctx, time_str):
    time = crf.check_valid_time(time_str)
    if not time:
      await ctx.send(f"Invalid time: {time_str}.")
      return
    dq_details = DQ.DailyQuestions_Details()
    dq_details.time = time
    global dq_time
    dq_time = time
    dq_details.write()
    await ctx.send(f"The time for daily questions has been set to {time_str}")
  
  @commands.command(name="dq.get_time")
  @is_dq_admin()
  async def dq_get_time(self, ctx):
    dq_details = DQ.DailyQuestions_Details()
    await ctx.send(f"The time for daily questions is {dq_details.time}.")
    pass
  
  @commands.command(name="dq.set_ques_chnl")
  @is_dq_admin()
  async def dq_set_ques_chnl(self, ctx, channel_str):
    channel = await cdf.check_valid_channel(self.bot, channel_str)
    if not channel:
      await ctx.send(f"Invalid channel: {channel_str}.")
      return
    dq_details = DQ.DailyQuestions_Details()
    dq_details.ques_chnl = int(channel_str)
    dq_details.write()
    await ctx.send(f"The channel for daily questions set to **{channel.category}** >> **{channel.name}** - {channel.id}.")
  
  @commands.command(name="dq.get_ques_chnl")
  @is_dq_admin()
  async def dq_get_ques_chnl(self, ctx):
    dq_details = DQ.DailyQuestions_Details()
    channel = await cdf.check_valid_channel(self.bot, dq_details.ques_chnl)
    await ctx.send(f"The channel for daily questions is **{channel.category}** >> **{channel.name}** - {channel.id}.")
  
  @commands.command(name="dq.set_soln_chnl")
  @is_dq_admin()
  async def dq_set_soln_chnl(self, ctx, channel_str):
    channel = await cdf.check_valid_channel(self.bot, channel_str)
    if not channel:
      await ctx.send(f"Invalid channel: {channel_str}.")
      return
    dq_details = DQ.DailyQuestions_Details()
    dq_details.soln_chnl = int(channel_str)
    dq_details.write()
    await ctx.send(f"The channel for the solutions set to **{channel.category}** >> **{channel.name}** - {channel.id}.")
  
  @commands.command(name="dq.get_soln_chnl")
  @is_dq_admin()
  async def dq_get_soln_chnl(self, ctx):
    dq_details = DQ.DailyQuestions_Details()
    channel = await cdf.check_valid_channel(self.bot, dq_details.soln_chnl)
    await ctx.send(f"The channel for the solutions is **{channel.category}** >> **{channel.name}** - {channel.id}.")
  
  @commands.command(name="dq.set_announcement_chnl")
  @is_dq_admin()
  async def dq_set_announcement_chnl(self, ctx, channel_str):
    if not await cdf.check_valid_channel (self.bot, channel_str):
      await ctx.send(f"Invalid channel: {channel_str}.")
      return
    dq_details = DQ.DailyQuestions_Details()
    dq_details.announcement_chnl = int(channel_str)
    dq_details.write()
  
  @commands.command(name="dq.get_announcement_chnl")
  @is_dq_admin()
  async def dq_get_announcement_chnl(self, ctx):
    dq_details = DQ.DailyQuestions_Details()
    channel = await cdf.check_valid_channel(self.bot, dq_details.announcement_chnl)
    await ctx.send(f"The channel for daily question announcements is {channel.category}: {channel.name} - {channel.id}.")
  
  @commands.command(name="dq.set_admin_chnl")
  @is_dq_admin()
  async def dq_set_admin_chnl(self, ctx, channel_str):
    channel = await cdf.check_valid_channel(self.bot, channel_str)
    if not channel:
      await ctx.send(f"Invalid channel: {channel_str}.")
      return
    dq_details = DQ.DailyQuestions_Details()
    dq_details.admin_chnl = int(channel_str)
    dq_details.write()
    await ctx.send(f"The channel for daily question administration set to {channel.category}: {channel.name} - {channel.id}.")
  
  @commands.command(name="dq.get_admin_chnl")
  @is_dq_admin()
  async def dq_get_admin_chnl(self, ctx):
    dq_details = DQ.DailyQuestions_Details()
    channel = await cdf.check_valid_channel(self.bot, dq_details.admin_chnl)
    await ctx.send(f"The channel for daily question administration is {channel.category}: {channel.name} - {channel.id}.")
  
  @commands.command(name="dq.set_admin_roles")
  @is_dq_admin()
  async def dq_set_admin_roles(self, ctx, admin_roles):
    admin_roles_str = admin_roles
    admin_roles = admin_roles.strip("[]")
    admin_roles = admin_roles.split(",") if admin_roles else []
    possible = True
    for x in range(len(admin_roles)):
      if not await cdf.check_valid_role(self.bot, ctx.guild_id, admin_roles[x]):
        await ctx.send(f"{admin_roles[x]} is not a valid role.")
        possible = False
    if not possible:
      return
    dq_details = DQ.DailyQuestions_Details()
    dq_details.admin_roles = admin_roles
    dq_details.write()
    global dq_admin_roles
    dq_admin_roles = admin_roles
    await ctx.send(f"The admin roles have been set to:\n{admin_roles_str}")
  
  @commands.command(name="dq.get_admin_roles")
  @is_dq_admin()
  async def dq_get_admin_roles(self, ctx):
    dq_details = DQ.DailyQuestions_Details()
    admin_roles_str = "["
    for x in dq_details.admin_roles:
      admin_roles_str += str(x) + ","
    admin_roles_str = admin_roles_str.strip(",") + "]"
    await ctx.send(f"The daily question admins are:\n{admin_roles_str}")
  
  @commands.command(name="dq.set_admin_users")
  @is_dq_admin()
  async def dq_set_admin_users(self, ctx, admin_users):
    admin_users_str = admin_users
    admin_users = admin_users.strip("[]")
    admin_users = admin_users.split(",") if admin_users else []
    possible = True
    for x in range(len(admin_users)):
      admin_users[x] = int(admin_users[x])
      if not await cdf.check_valid_user(self.bot, admin_users[x]):
        await ctx.send(f"{admin_users[x]} is not a valid user.")
        possible = False
    if not possible:
      return
    dq_details = DQ.DailyQuestions_Details()
    dq_details.admin_users = admin_users
    dq_details.write()
    global dq_admin_users
    dq_admin_users = admin_users
    await ctx.send(f"The admins have been set to:\n{admin_users_str}")
  
  @commands.command(name="dq.get_admin_users")
  @is_dq_admin()
  async def dq_get_admin_users(self, ctx):
    dq_details = DQ.DailyQuestions_Details()
    admin_users_str = "["
    for x in dq_details.admin_users:
      admin_users_str += str(x) + ","
    admin_users_str = admin_users_str.strip(",") + "]"
    await ctx.send(f"The daily question admins are:\n{admin_users_str}")
  
  @commands.command(name="dq.reset_posted")
  @is_dq_admin()
  async def dq_reset_posted(self, ctx, date):
    date = crf.check_valid_date(date)
    if not date:
      await ctx.send("Invalid Date!")
      return
    file = open(dq_questions_posted_file, "r")
    file_data = file.read()
    file.close()
    if "<" + date.strftime('%Y-%m-%d') + ">" not in file_data:
      await ctx.send(f"Questions were not posted on {date.strftime('%Y-%m-%d')}.")
      return
    file_data = csf.replace(file_data, "<" + date.strftime('%Y-%m-%d') + ">", count=1)
    file = open(dq_questions_posted_file, "w")
    file.write(file_data)
    file.close()
    await ctx.send(f"Reset posted question tracker for {date.strftime('%Y-%m-%d')}.")
  
  @commands.command(name="dq.announce_ques_and_soln")
  @is_dq_admin()
  async def dq_announce_ques_and_soln(self, ctx):
    await announce_questions_and_soln(self.bot)
  
  @tasks.loop(seconds=45)
  async def check_dq_time(self):
    curr_time = datetime.now() + timedelta(hours=5, minutes=30)
    if dq_time.strftime('%H:%M') == curr_time.strftime('%H:%M'):
      print(f"dq: {dq_time.strftime('%H:%M')} now: {curr_time.strftime('%H:%M')} Now is the time!")
      await announce_questions_and_soln(self.bot)
    else:
      print(f"dq: {dq_time.strftime('%H:%M')} now: {curr_time.strftime('%H:%M')}")
  
  @check_dq_time.before_loop
  async def before_check_dq_time(self):
    global dq_time
    dq_details = DQ.DailyQuestions_Details()
    dq_time = dq_details.time
    await self.bot.wait_until_ready()

async def setup(bot):
  await bot.add_cog(DailyQuestions_Cog(bot))

def get_nth_or_date(date):
  if isinstance(date, str) and not date.isdigit():
    date = crf.check_valid_date(date)
    return date
  elif isinstance(date, str):
    return int(date)
  elif isinstance(date, int):
    return date
  else:
    return False

async def announce_questions_and_soln(bot):
  date = (datetime.now() + timedelta(hours=5, minutes=30))
  file = open(dq_questions_posted_file, "r")
  ques_posted = file.read()
  file.close()
  dq_details = DQ.DailyQuestions_Details()
  admin_chnl = await cdf.check_valid_channel(bot, dq_details.admin_chnl)
  if "<" + date.strftime('%Y-%m-%d %H:%M') + ">" in ques_posted:
    print(f"Questions for {date.strftime('%Y-%m-%d %H:%M')} have already been posted.")
    await admin_chnl.send(f"Questions for {date.strftime('%Y-%m-%d %H:%M')} have aready been posted.")
    return
  ques_posted += "\n" + "<" + date.strftime('%Y-%m-%d %H:%M') + ">"
  file = open(dq_questions_posted_file, "w")
  file.write(ques_posted)
  file.close()
  date = crf.check_valid_date(date)
  prev_date = date - timedelta(days=1)
  dq = DQ.DailyQuestions()
  day_list = dq.get_day_list()
  
  questions_found = True
  if date not in day_list[0]:
    questions_found = False
    print(f"Questions for {date.strftime('%Y-%m-%d')} were not found.")
    await admin_chnl.send(f"Daily Questions for {date.strftime('%Y-%m-%d')} were not found.")
  if (prev_date) in day_list[0]:
    if (questions_found and day_list[0][date] == day_list[0][prev_date]): # means that today is a continuation of a prev set
      print(f"Today is not the day to post fresh questions.")
      return
    else: # means that today is a fresh set so post prev day's soln
      await announce_soln(bot, dq.get_day(prev_date), dq_details.soln_chnl)
  else:
    print(f"Solutions for day before {date.strftime('%Y-%m-%d')} were not found.")
    await admin_chnl.send(f"DQ **Solutionss** for day before {date.strftime('%Y-%m-%d')} were not found.")
    
  if not questions_found:
    return
  await announce_ques(bot, dq.get_day(date), dq_details.ques_chnl)

async def announce_ques(bot, day: DQ.DailyQuestions_Day, channel: int):
  ques_msg = day.to_announce_ques()
  ques_chnl = await cdf.check_valid_channel(bot, channel)
  await ques_chnl.send(ques_msg["title"])
  for x in ques_msg["questions"]:
    msg = await ques_chnl.send(x)
    await msg.add_reaction(emojis.white_check_mark)

async def announce_soln(bot, day: DQ.DailyQuestions_Day, channel: int):
  soln_msg = day.to_announce_soln()
  soln_chnl = await cdf.check_valid_channel(bot, channel)
  await soln_chnl.send(soln_msg["title"])
  for x in soln_msg["questions"]:
    msg = ""
    for y in x:
      msg = await soln_chnl.send(y)
    await msg.add_reaction(emojis.sparkles)