import os
from datetime import datetime
import custom_string_functions as csf
from Data import emojis
import config_reader as cr

class Question:

  def __init__(self, level, link, note, nth = 0):
    self.level = get_level(level)
    self.link = link
    self.note = note
    self.nth = nth


class DailyQuestions_Day:

  def __init__(self, date: datetime, nth = 0):
    self.date = date
    self.nth = nth
    self.ques = []

  def add_question(self, new_ques: Question):
    self.ques.append(new_ques)

  def arrange(self):
    self.ques.sort(key = lambda x: x.nth)


class DailyQuestions_All:

  def __init__(self):
    self.days = []

  def add_day(self, new_day: DailyQuestions_Day):
    self.days.append(new_day)

  def arrange_days(self):
    self.days.sort(key=lambda x: x.nth)


def read_daily_question(date : datetime):
  file_data = cr.encrypted_file_read(daily_ques_file)

  DailyQuestions_RETURN = DailyQuestions_All()

  while "# " in file_data:
    temp_str = csf.str_after(file_data, "# ")
    file_data = csf.str_before(file_data, "# ")
    if "\n" in temp_str:
      file_data += csf.str_after(temp_str, "\n")

  date_str = "date=" + date.strftime("%d-%m-%Y")
  while "</dq>" in file_data:
    CurrentDay_str = csf.str_in_bw(file_data, "<dq", "</dq>", 1)
    file_data = csf.str_after(file_data, "</dq>")

    if date_str not in CurrentDay_str:
      continue
    CurrentDay = DailyQuestions_Day(date, int(csf.str_in_bw(CurrentDay_str, "<dq", ">")))
    while "</q>" in CurrentDay_str:
      curr_ques_nth = csf.str_in_bw(CurrentDay_str, "<q", ">")
      curr_ques_nth.strip("\n\r\t ")
      curr_ques_level = csf.str_in_bw(CurrentDay_str, "level=", "\n")
      curr_ques_level.strip("\n\r\t ")
      curr_ques_link = csf.str_in_bw(CurrentDay_str, "link=", "\n")
      curr_ques_link.strip("\n\r\t ")
      curr_ques_note = csf.str_in_bw(CurrentDay_str, "note=", "\n")
      curr_ques_note.strip("\n\r\t ")
      CurrentDay.add_question(Question(curr_ques_level, curr_ques_link, curr_ques_note, int(curr_ques_nth)))
      CurrentDay_str = csf.str_after(CurrentDay_str, "</q>")
    CurrentDay.arrange()
    DailyQuestions_RETURN.add_day(CurrentDay)
    break
  return DailyQuestions_RETURN

async def print_questions(ctx, CurrentDay: DailyQuestions_Day):
  await ctx.send(
      f"**DAILY PROBLEMS (DAY {CurrentDay.nth}) - {CurrentDay.date.strftime('%d-%m-%Y')}**"
  )
  for x in CurrentDay.ques:
    msg = ""
    if x.note:
      msg = await ctx.send(f"**{x.level}:** <{x.link}>\nNote:{x.note}")
    else:
      msg = await ctx.send(f"**{x.level}:** <{x.link}>")
    await msg.add_reaction(emojis.white_check_mark)

async def get_print_questions(ctx, date : datetime):
  DailyQuestionsList = read_daily_question(date)
  if DailyQuestionsList.days:
    await print_questions(ctx, DailyQuestionsList.days[0])
  else:
    await ctx.send(f"Questions for {date.strftime('%d-%m-%Y')} were not found.")

def get_time():
  file_data = cr.encrypted_file_read(daily_ques_file)

  if "<time>" not in file_data:
    return False

  return csf.str_in_bw(file_data, "<time>", "</time>")

def get_channel_id():
  file_data = cr.encrypted_file_read(daily_ques_file)

  if "<dq_channel>" not in file_data:
    return False

  return csf.str_in_bw(file_data, "<dq_channel>", "</dq_channel>")

def set_time(time : datetime):
  file_data = cr.encrypted_file_read(daily_ques_file)
  temp_str = csf.str_in_bw(file_data, "<time>", "</time>", 1)
  file_data = csf.str_replace(file_data, temp_str, "<time>" + time.strftime("%H:%M") + "</time>")
  cr.encrypted_file_write(daily_ques_file, file_data)

def set_channel(channel):
  file_data = cr.encrypted_file_read(daily_ques_file)
  temp_str = csf.str_in_bw(file_data, "<dq_channel>", "</dq_channel>", 1)
  file_data = csf.str_replace(file_data, temp_str, "<dq_channel>" + channel + "</dq_channel>")
  cr.encrypted_file_write(daily_ques_file, file_data)

def get_level(level):
  if level in ["Cakewalk", "Easy", "Medium", "Hard", "Giveup"]:
    return level
  elif (level == 'C'):
    return "Cakewalk"
  elif (level == 'E'):
    return "Easy"
  elif (level == 'M'):
    return "Medium"
  elif (level == 'H'):
    return "Hard"
  elif (level == 'G'):
    return "Giveup"
  elif (level == "CE"):
    return "Cakewalk-Easy"
  elif (level == "EM"):
    return "Easy-Medium"
  elif (level == "MH"):
    return "Medium-Hard"
  elif (level == "HG"):
    return "Hard-Giveup"
  else:
    return "Not Defined"

def str_to_datetime(date):
  day = csf.str_before(date, "-")
  date = csf.str_after(date, "-")
  month = csf.str_before(date, "-")
  year = csf.str_after(date, "-")
  if (len(year) == 2):
    year = "20" + year
  try:
    date = datetime(int(year), int(month), int(day))
  except:
    return False
  return date

async def check_existing_day(file_data, CurrentDay : DailyQuestions_Day):
  curr_day_nth = CurrentDay.nth
  curr_day_date = CurrentDay.date.strftime('%d-%m-%Y')
  
  details = {"day_exists": False, "same_nth": False, "same_date": False, "nth_and_date_diff": False}
  
  pos = file_data.find("<dq" + curr_day_nth + ">")
  if (pos != -1):
    details_ = {"nth_value": curr_day_nth, "date_value": 0}
    day_with_nth = csf.str_after(file_data, "<dq" + curr_day_nth + ">", 1)
    date = csf.str_in_bw(day_with_nth, "date=", "\n")
    date = str_to_datetime(date)
    details_["date_value"] = date
    details["same_nth"] = details_
  
  pos = file_data.find("date=" + curr_day_date)
  if (pos != -1):
    date = str_to_datetime(curr_day_date)
    details_ = {"nth_value": 0, "date_value": date}
    day_with_date
    
def day_from_date():
  

async def add_question_day(ctx, CurrentDay : DailyQuestions_Day):
  file_data = cr.encrypted_file_read(daily_ques_file)
  if check_existing_day(file_data, CurrentDay):
    return

def daily_ques_file_read():
  file_data = cr.encrypted_file_read(daily_ques_file)
  return file_data

class DailyQuestions_File:
  def __init__(self):
    self.file_path = "/home/runner/Shot/Data/daily_questions.config"
    self.file_data = ""
  
  def read(self):
    self.file_data = cr.encrypted_file_read(self.file_path)
  
  def write(self):
    cr.encrypted_file_write(self.file_path, self.file_data)
  
  def nth_and_date(self):
    