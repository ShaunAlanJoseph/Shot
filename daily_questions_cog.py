from discord.ext import commands, tasks
import custom_string_functions as csf
import custom_random_functions as crf
import custom_discord_functions as cdf
import daily_questions as dq
from datetime import datetime, timedelta
from Data import emojis

dq_admin_users = []
dq_admin_roles = []
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
    dqf = dq.DailyQuestions_File()
    global dq_admin_users, dq_admin_roles, dq_time
    dq_admin_users = dqf.details.admin_users
    dq_admin_roles = dqf.details.admin_roles
    dq_time = dqf.details.time
    self.check_dq_time.start()
  
  @commands.command(name="dq.ping", description="Pongs you...duh!")
  @is_dq_admin()
  async def dq_ping(self, ctx):
    await ctx.send(f"{ctx.author.mention} pong!!")
  
  @commands.command(name="dq.add")
  @is_dq_admin()
  async def dq_add(self, ctx):
    msg = ctx.message.content
    msg = csf.str_after(msg, "```")
    msg = csf.str_before(msg, "```")
    dqf = dq.DailyQuestions_File()
    new_day = dq.DailyQuestions_Day(msg)
    if dqf.write_new_day(new_day):
      await ctx.send(f"Questions for ({new_day.nth}) {new_day.date.strftime('%d-%m-%Y')} have been added.")
    else:
      await ctx.send(f"({new_day.nth}) {new_day.date.strftime('%d-%m-%Y')} -> Clashes with an existing day.")
  
  @commands.command(name="dq.remove")
  @is_dq_admin()
  async def dq_remove(self, ctx, day):
    day = get_nth_or_date(day)
    if not day:
      await ctx.send(f"Invalid Date!")
      return
    
    dqf = dq.DailyQuestions_File()
    removed_day = dqf.remove_day(day)
    if removed_day:
      await ctx.send(f"Questions for ({removed_day['day'].nth}) {removed_day['day'].date.strftime('%d-%m-%Y')} have been removed.\nRaw:\n```{removed_day['raw']}```")
    else:
      if isinstance(day, datetime):
        await ctx.send(f"Questions for {day.strftime('%d-%m-%Y')} were not found.")
      else:
        await ctx.send(f"Questions for Day {day} were not found.")
  
  @commands.command(name="dq.replace")
  @is_dq_admin()
  async def dq_replace(self, ctx, old_day):
    old_day = get_nth_or_date(old_day)
    if not old_day:
      await ctx.send(f"Invalid Date!")
      return
    
    msg = ctx.message.content
    msg = csf.str_after(msg, "```")
    msg = csf.str_before(msg, "```")
    new_day = dq.DailyQuestions_Day(msg)
    
    dqf = dq.DailyQuestions_File()
    old_day = dqf.replace_day(old_day, new_day)
    if old_day:
      await ctx.send(f"Day ({old_day['day'].nth}) {old_day['day'].date.strftime('%d-%m-%Y')} replaced with ({new_day.nth}) {new_day.date.strftime('%d-%m-%Y')}.\nOld Day Raw:\n```{old_day['raw']}```")
    else:
      await ctx.send(f"There was an error replacing the day.")
  
  @commands.command(name="dq.list_days")
  @is_dq_admin()
  async def dq_list_days(self, ctx):
    dqf = dq.DailyQuestions_File()
    day_list = dqf.get_day_list()
    msg = ""
    for x in day_list:
      msg += str(x[0]) + " -> " + x[1].strftime('%d-%m-%Y') + "\n"
    await ctx.send(f"Here is a list of days:\n{msg}")
  
  @commands.command(name="dq.day_raw")
  @is_dq_admin()
  async def dq_day_raw(self, ctx, day):
    day = get_nth_or_date(day)
    if not day:
      await ctx.send(f"Invalid Date!")
      return
    
    dqf = dq.DailyQuestions_File()
    DailyQuestions = dqf.get_questions()
    if day in DailyQuestions.days:
      day = DailyQuestions.days[day]
      msg = day.to_str()
      await ctx.send(f"Questions for ({day.nth}) {day.date.strftime('%d-%m-%Y')}:\n```\n{msg}\n```")
    else:
      if isinstance(day, int):
        await ctx.send(f"Questions for Day {day} were not found.")
      else:
        await ctx.send(f"Questions for {day.strftime('%d-%m-%Y')} were not found.")
  
  @commands.command(name="dq.announce_ques")
  @is_dq_admin()
  async def dq_announce_ques(self, ctx, date):
    day = get_nth_or_date(date)
    if not day:
      await ctx.send(f"Invalid Date!")
      return

    dqf = dq.DailyQuestions_File()
    DailyQuestions = dqf.get_questions()
    if day in DailyQuestions.days:
      await announce_ques(self.bot, DailyQuestions.days[day], dqf.details.ques_chnl)
    else:
      if isinstance(date, int):
        await ctx.send(f"Questions for Day {date} were not found.")
      else:
        await ctx.send(f"Questions for {date.strftime('%d-%m-%Y')} were not found.")
  
  @commands.command(name="dq.announce_soln")
  @is_dq_admin()
  async def dq_announce_soln(self, ctx, date):
    day = get_nth_or_date(date)
    if not day:
      await ctx.send(f"Invalid Date!")
      return

    dqf = dq.DailyQuestions_File()
    DailyQuestions = dqf.get_questions()
    if day in DailyQuestions.days:
      await announce_soln(self.bot, DailyQuestions.days[day], dqf.details.soln_chnl)
    else:
      if isinstance(date, int):
        await ctx.send(f"Solutions for Day {date} were not found.")
      else:
        await ctx.send(f"Solutions for {date.strftime('%d-%m-%Y')} were not found.")
  
  @commands.command(name="dq.day_format")
  @is_dq_admin()
  async def dq_day_format(self, ctx):
    day_format = """```
    <dq>
    <nth></nth>
    <date></date>
    <q>
    <q_n>1</q_n>
    <q_lvl></q_lvl>
    <q_link></q_link>
    <q_note></q_note>
    <q_soln></q_soln>
    </q>
    <q>
    <q_n>2</q_n>
    <q_lvl></q_lvl>
    <q_link></q_link>
    <q_note></q_note>
    <q_soln></q_soln>
    </q>
    </dq>```"""
    await ctx.send(f"{day_format}")
  
  @commands.command(name="dq.set_time")
  @is_dq_admin()
  async def dq_set_time(self, ctx, time_str):
    time = crf.check_valid_time(time_str)
    if not time:
      await ctx.send(f"Invalid time: {time_str}.")
      return
    dqf = dq.DailyQuestions_File()
    dqf.details.time = time.strftime('%H:%M')
    global dq_time
    dq_time = dqf.details.time
    dqf.write_details()
    await ctx.send(f"The time for daily questions has been set to {time_str}")
  
  @commands.command(name="dq.get_time")
  @is_dq_admin()
  async def dq_get_time(self, ctx):
    dqf = dq.DailyQuestions_File()
    await ctx.send(f"The time for daily questions is {dqf.details.time}.")
    pass
  
  @commands.command(name="dq.set_ques_chnl")
  @is_dq_admin()
  async def dq_set_ques_chnl(self, ctx, channel_str):
    channel = await cdf.check_valid_channel(self.bot, channel_str)
    if not channel:
      await ctx.send(f"Invalid channel: {channel_str}.")
      return
    dqf = dq.DailyQuestions_File()
    dqf.details.ques_chnl = int(channel_str)
    dqf.write_details()
    await ctx.send(f"The channel for daily questions set to **{channel.category}** >> **{channel.name}** - {channel.id}.")
  
  @commands.command(name="dq.get_ques_chnl")
  @is_dq_admin()
  async def dq_get_ques_chnl(self, ctx):
    dqf = dq.DailyQuestions_File()
    channel = await cdf.check_valid_channel(self.bot, dqf.details.ques_chnl)
    await ctx.send(f"The channel for daily questions is **{channel.category}** >> **{channel.name}** - {channel.id}.")
  
  @commands.command(name="dq.set_soln_chnl")
  @is_dq_admin()
  async def dq_set_soln_chnl(self, ctx, channel_str):
    channel = await cdf.check_valid_channel(self.bot, channel_str)
    if not channel:
      await ctx.send(f"Invalid channel: {channel_str}.")
      return
    dqf = dq.DailyQuestions_File()
    dqf.details.soln_chnl = int(channel_str)
    dqf.write_details()
    await ctx.send(f"The channel for the solutions set to **{channel.category}** >> **{channel.name}** - {channel.id}.")
  
  @commands.command(name="dq.get_soln_chnl")
  @is_dq_admin()
  async def dq_get_soln_chnl(self, ctx):
    dqf = dq.DailyQuestions_File()
    channel = await cdf.check_valid_channel(self.bot, dqf.details.soln_chnl)
    await ctx.send(f"The channel for the solutions is **{channel.category}** >> **{channel.name}** - {channel.id}.")
  
  @commands.command(name="dq.set_announcement_chnl")
  @is_dq_admin()
  async def dq_set_announcement_chnl(self, ctx, channel_str):
    if not await cdf.check_valid_channel (self.bot, channel_str):
      await ctx.send(f"Invalid channel: {channel_str}.")
      return
    dqf = dq.DailyQuestions_File()
    dqf.details.announcement_chnl = int(channel_str)
    dqf.write_details()
  
  @commands.command(name="dq.get_announcement_chnl")
  @is_dq_admin()
  async def dq_get_announcement_chnl(self, ctx):
    dqf = dq.DailyQuestions_File()
    channel = await cdf.check_valid_channel(self.bot, dqf.details.announcement_chnl)
    await ctx.send(f"The channel for daily question announcements is {channel.category}: {channel.name} - {channel.id}.")
  
  @commands.command(name="dq.set_admin_chnl")
  @is_dq_admin()
  async def dq_set_admin_chnl(self, ctx, channel_str):
    channel = await cdf.check_valid_channel(self.bot, channel_str)
    if not channel:
      await ctx.send(f"Invalid channel: {channel_str}.")
      return
    dqf = dq.DailyQuestions_File()
    dqf.details.admin_chnl = int(channel_str)
    dqf.write_details()
    await ctx.send(f"The channel for daily question administration set to {channel.category}: {channel.name} - {channel.id}.")
  
  @commands.command(name="dq.get_admin_chnl")
  @is_dq_admin()
  async def dq_get_admin_chnl(self, ctx):
    dqf = dq.DailyQuestions_File()
    channel = await cdf.check_valid_channel(self.bot, dqf.details.admin_chnl)
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
    dqf = dq.DailyQuestions_File()
    dqf.details.admin_roles = admin_roles
    dqf.write_details()
    global dq_admin_roles
    dq_admin_roles = admin_roles
    await ctx.send(f"The admin roles have been set to:\n{admin_roles_str}")
  
  @commands.command(name="dq.get_admin_roles")
  @is_dq_admin()
  async def dq_get_admin_roles(self, ctx):
    dqf = dq.DailyQuestions_File()
    admin_roles_str = "["
    for x in dqf.details.admin_roles:
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
    dqf = dq.DailyQuestions_File()
    dqf.details.admin_users = admin_users
    dqf.write_details()
    global dq_admin_users
    dq_admin_users = admin_users
    await ctx.send(f"The admins have been set to:\n{admin_users_str}")
  
  @commands.command(name="dq.get_admin_users")
  @is_dq_admin()
  async def dq_get_admin_users(self, ctx):
    dqf = dq.DailyQuestions_File()
    admin_users_str = "["
    for x in dqf.details.admin_users:
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
    if "<" + date.strftime('%d-%m-%Y') + ">" not in file_data:
      await ctx.send(f"Questions were not posted on {date.strftime('%d-%m-%Y')}.")
      return
    file_data = csf.str_replace(file_data, "<" + date.strftime('%d-%m-%Y') + ">", count=1)
    file = open(dq_questions_posted_file, "w")
    file.write(file_data)
    file.close()
    await ctx.send(f"Reset posted question tracker for {date.strftime('%d-%m-%Y')}.")
  
  @commands.command(name="dq.announce_ques_and_soln")
  @is_dq_admin()
  async def dq_announce_ques_and_soln(self, ctx):
    await announce_questions_and_soln(self.bot)
  
  @tasks.loop(seconds=45)
  async def check_dq_time(self):
    dq_time = dq.get_dq_time()
    curr_time = datetime.now() + timedelta(hours=5, minutes=30)
    if dq_time.strftime('%H:%M') == curr_time.strftime('%H:%M'):
      print(f"dq: {dq_time.strftime('%H:%M')} now: {curr_time.strftime('%H:%M')} Now is the time!")
      await announce_questions_and_soln(self.bot)
    else:
      print(f"dq: {dq_time.strftime('%H:%M')} now: {curr_time.strftime('%H:%M')}")
  
  @check_dq_time.before_loop
  async def before_check_dq_time(self):
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
  date = (datetime.now() + timedelta(hours=5, minutes=30)).strftime('%d-%m-%Y')
  file = open(dq_questions_posted_file, "r")
  ques_posted = file.read()
  file.close()
  dqf = dq.DailyQuestions_File()
  admin_chnl = await cdf.check_valid_channel(bot, dqf.details.admin_chnl)
  if "<" + date + ">" in ques_posted:
    print(f"Questions for {date} have already been posted.")
    await admin_chnl.send(f"Questions for {date} have aready been posted.")
    return
  ques_posted += "\n" + "<" + date + ">"
  file = open(dq_questions_posted_file, "w")
  file.write(ques_posted)
  file.close()
  date = crf.check_valid_date(date)
  DailyQuestions = dqf.get_questions()
  
  questions_found = True
  if date not in DailyQuestions.days:
    questions_found = False
    print(f"Questions for {date.strftime('%d-%m-%Y')} were not found.")
    await admin_chnl.send(f"Daily Questions for {date.strftime('%d-%m-%Y')} were not found.")
  
  soln_found = False
  soln_date = date
  while True:
    soln_date = soln_date - timedelta(days=1)
    if soln_date in DailyQuestions.days:
      soln_found = True
      break
    elif soln_date < crf.check_valid_date("15-12-2023"):
      break
  if soln_found:
    await announce_soln(bot, DailyQuestions.days[soln_date], dqf.details.soln_chnl)
  else:
    print(f"Solutions for a day prior to {date.strftime('%d-%m-%Y')} were not found.")
    await admin_chnl.send(f"Daily Questions **Solutionss** for {date.strftime('%d-%m-%Y')} were not found.")
  
  if not questions_found:
    return
  await announce_ques(bot, DailyQuestions.days[date], dqf.details.ques_chnl)

async def announce_ques(bot, day: dq.DailyQuestions_Day, channel: int):
  ques_msg = day.to_announce_ques()
  ques_chnl = await cdf.check_valid_channel(bot, channel)
  await ques_chnl.send(ques_msg["title"])
  for x in ques_msg["questions"]:
    msg = await ques_chnl.send(x)
    await msg.add_reaction(emojis.white_check_mark)

async def announce_soln(bot, day: dq.DailyQuestions_Day, channel: int):
  soln_msg = day.to_announce_soln()
  soln_chnl = await cdf.check_valid_channel(bot, channel)
  await soln_chnl.send(soln_msg["title"])
  for x in soln_msg["questions"]:
    msg = ""
    for y in x:
      msg = await soln_chnl.send(y)
    await msg.add_reaction(emojis.sparkles)