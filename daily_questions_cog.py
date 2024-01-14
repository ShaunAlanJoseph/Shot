from discord.ext import commands, tasks
import custom_string_functions as csf
import custom_random_functions as crf
import custom_discord_functions as cdf
import daily_questions as DQ
from datetime import datetime, timedelta
from Data import emojis
import pastebin_reader as pr
import traceback

dq_admin_users = set()
dq_admin_roles = set()
dq_time = ""

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
    dq_settings = DQ.DailyQuestions_Settings()
    global dq_admin_users, dq_admin_roles, dq_time
    for x in dq_settings.admin_users:
      dq_admin_users.add(x)
    for x in dq_settings.admin_roles:
      dq_admin_roles.add(x)
    dq_time = dq_settings.time
    self.check_dq_time.start()
  
  async def cog_command_error(self, ctx, error):
    traceback.print_exc()
    await ctx.reply(f"Error: {error}.")
  
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
      await ctx.reply(f"Questions for ({new_day.nth}) {new_day.start_date.strftime('%Y-%m-%d')} have been added.", mention_author=False)
    except Exception as ex:
      traceback.print_exc()
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
      await ctx.reply(f"Removed day: ({removed_day['day'].nth}) {removed_day['day'].start_date.strftime('%Y-%m-%d')}.\n**Raw:**\n```\n{removed_day['raw']}\n```", mention_author=False)
    except Exception as ex:
      traceback.print_exc()
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
      await ctx.reply(f"Removed day: ({removed_day['day'].nth}) {removed_day['day'].start_date.strftime('%Y-%m-%d')}.\n**Raw:**\n```\n{removed_day['raw']}\n```", mention_author=False)
    
      msg = ctx.message.content
      msg = csf.after(msg, "```")
      msg = csf.before(msg, "```")
      new_day = DQ.DailyQuestions_Day(msg, True)
    
      new_day = dq.add_day(msg)
      await ctx.reply(f"Questions for ({new_day.nth}) {new_day.start_date.strftime('%Y-%m-%d')} have been added.", mention_author=False)
    except Exception as ex:
      traceback.print_exc()
      await ctx.reply(f"Error: {ex}")
  
  @commands.command(name="dq.list_days")
  @is_dq_admin()
  async def dq_list_days(self, ctx):
    try:
      dq = DQ.DailyQuestions()
      day_list = dq.get_day_list()
      msg = ""
      for i in range(1, len(day_list)):
        msg += f"{day_list[i]['nth']}) -> {day_list[i]['start'].strftime('%Y-%m-%d')} ({day_list[i]['duration']})\n"
      await ctx.reply(f"Here is a list of days:\n{msg}", mention_author=False)
    except Exception as ex:
      traceback.print_exc()
      await ctx.reply(f"Error: {ex}")
  
  @commands.command(name="dq.get_day_raw")
  @is_dq_admin()
  async def dq_get_day_raw(self, ctx, day):
    day = get_nth_or_date(day)
    if not day:
      await ctx.reply(f"Invalid Day!")
      return
    
    dq = DQ.DailyQuestions()
    try:
      curr_day_raw = dq.get_day_raw(day)
      await ctx.reply(f"```\n{curr_day_raw}\n```", mention_author=False)
    except Exception as ex:
      traceback.print_exc()
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
      dq_settings = DQ.DailyQuestions_Settings()
      await announce_ques(self.bot, day, dq_settings.ques_chnl)
    except Exception as ex:
      if (ex.__class__.__name__ == "DailyQuestions_Day_FileNotFound"):
        print(f"Day doesn't exist: {date}!")
        await ctx.reply(f"Day doesn't exist: {date}")
      else:
        traceback.print_exc()
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
      dq_settings = DQ.DailyQuestions_Settings()
      await announce_soln(self.bot, day, dq_settings.soln_chnl)
    except Exception as ex:
      if (ex.__class__.__name__ == "DailyQuestions_Day_FileNotFound"):
        print(f"Day doesn't exist: {date}!")
        await ctx.reply(f"Day doesn't exist: {date}")
      else:
        traceback.print_exc()
        await ctx.reply(f"Error: {ex}")
  
  @commands.command(name="dq.get_day_format")
  @is_dq_admin()
  async def dq_get_day_format(self, ctx):
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
    await ctx.reply(f"{day_format}", mention_author=False)
    
  @commands.command(name="dq.set_settings")
  @is_dq_admin()
  async def dq_set_details(self, ctx):
    msg = ctx.message.content
    msg = csf.after(msg, "```")
    msg = csf.before(msg, "```")
    dq_settings = DQ.DailyQuestions_Settings(msg)
    dq_settings.write()
    global dq_admin_users, dq_admin_roles, dq_time
    for x in dq_settings.admin_users:
      dq_admin_users.add(x)
    for x in dq_settings.admin_roles:
      dq_admin_roles.add(x)
    dq_time = dq_settings.time
    await ctx.reply(f"Daily Questions settings have been set.", mention_author=False)
  
  @commands.command(name="dq.get_settings")
  @is_dq_admin()
  async def dq_get_settings(self, ctx):
    dq_settings = DQ.DailyQuestions_Settings()
    await ctx.reply(f"Current settings for Daily Questions:\n```{dq_settings.to_str()}\n```", mention_author=False)
  
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
    dq_settings = DQ.DailyQuestions_Settings()
    dq_time = dq_settings.time
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
  try:
    date = (datetime.now() + timedelta(hours=5, minutes=30))
    pbm = pr.PasteBin_main()
    ques_posted = pbm.get_file(pbm.main["dq"]["ques_posted"])
    dq_settings = DQ.DailyQuestions_Settings()
    admin_chnl = await cdf.check_valid_channel(bot, dq_settings.admin_chnl)
    if "<" + date.strftime('%Y-%m-%d %H:%M') + ">" in ques_posted:
      print(f"Questions for {date.strftime('%Y-%m-%d %H:%M')} have already been posted.")
      await admin_chnl.send(f"Questions for {date.strftime('%Y-%m-%d %H:%M')} have aready been posted.")
      return
    ques_posted += "\n" + "<" + date.strftime('%Y-%m-%d %H:%M') + ">"
    pbm.edit_dq_file("ques_posted", ques_posted)
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
        await announce_soln(bot, dq.get_day(prev_date), dq_settings.soln_chnl)
    else:
      print(f"Solutions for day before {date.strftime('%Y-%m-%d')} were not found.")
      await admin_chnl.send(f"DQ **Solutionss** for day before {date.strftime('%Y-%m-%d')} were not found.")

    if not questions_found:
      return
    await announce_ques(bot, dq.get_day(date), dq_settings.ques_chnl)
  except Exception as ex:
    traceback.print_exc()

async def announce_ques(bot, day: DQ.DailyQuestions_Day, channel: int):
  try:
    ques_msg = day.to_announce_ques()
    ques_chnl = await cdf.check_valid_channel(bot, channel)
    await ques_chnl.send(ques_msg["title"])
    for x in ques_msg["questions"]:
      msg = await ques_chnl.send(x)
      await msg.add_reaction(emojis.white_check_mark)
  except Exception as ex:
    traceback.print_exc()

async def announce_soln(bot, day: DQ.DailyQuestions_Day, channel: int):
  try:
    soln_msg = day.to_announce_soln()
    soln_chnl = await cdf.check_valid_channel(bot, channel)
    await soln_chnl.send(soln_msg["title"])
    for x in soln_msg["questions"]:
      msg = ""
      for y in x:
        msg = await soln_chnl.send(y)
      await msg.add_reaction(emojis.sparkles)
  except Exception as ex:
    traceback.print_exc()