from datetime import datetime
import custom_string_functions as csf
import custom_random_functions as crf
from Data import emojis
import config_reader as cr

class DailyQuestions_Question:

  def __init__(self, nth: int, level, link, note, soln):
    self.nth = nth
    self.level = get_level(level)
    self.link = link
    self.note = note
    self.soln = soln
  
  def __init__(self, curr_ques_str: str):
    self.nth = int(csf.str_in_bw(curr_ques_str, "<nth>", "</nth>"))
    self.level = csf.str_in_bw(curr_ques_str, "<level>", "</level>")
    self.level = get_level(self.level)
    self.link = csf.str_in_bw(curr_ques_str, "<link>", "</link>")
    self.note = csf.str_in_bw(curr_ques_str, "<note>", "</note>")
    self.soln = csf.str_in_bw(curr_ques_str, "<soln>", "</soln>")

class DailyQuestions_Day:

  def __init__(self, nth: int, date: datetime):
    self.date = date
    self.nth = nth
    self.ques = []
  
  def __init__(self, curr_day_str: str):
    self.nth = int(csf.str_in_bw(curr_day_str, "<nth>", "</nth>"))
    self.date = crf.check_valid_date(csf.str_in_bw(curr_day_str, "<date>", "</date>"))
    self.ques = []
    while "</q>" in curr_day_str:
      curr_ques_str = csf.str_in_bw(curr_day_str, "<q>", "</q>")
      curr_day_str = csf.str_after(curr_day_str, "</q>")
      curr_ques = DailyQuestions_Question(curr_ques_str)
      self.add_question(curr_ques)

  def add_question(self, new_ques: DailyQuestions_Question):
    self.ques.append(new_ques)
    
  def to_str(self):
    day_str = "<dq>\n"
    day_str += "<nth>" + str(self.nth) + "</nth>\n"
    day_str += "<date>" + self.date.strftime('%d-%m-%Y') + "</date>\n"
    for curr_ques in self.ques:
      day_str += "<q>\n"
      day_str += "<nth>" + str(curr_ques.nth) + "</nth>\n"
      day_str += "<level>" + curr_ques.level + "</level>\n"
      day_str += "<link>" + curr_ques.link + "</link>\n"
      day_str += "<note>" + curr_ques.note + "</note>\n"
      day_str += "<soln>" + curr_ques.soln + "</soln>\n"
      day_str += "</q>\n"
    day_str += "</dq>\n"
    return day_str

  def arrange(self):
    self.ques.sort(key = lambda x: x.nth)
  
  def to_announce_ques(self):
    msg = {}
    msg["title"] = f"**DAILY PROBLEMS (DAY{self.nth}) - {self.date.strftime('%d-%m-%Y')}**"
    msg["questions"] = []
    for x in self.ques:
      ques_msg = f"**{x.nth}) {x.level}:** <{x.link}>"
      if x.note:
        ques_msg += f"Note: {x.note}"
      msg["questions"].append(ques_msg)
    return msg
  
  def to_announce_soln(self):
    msg = {}
    msg["title"] = f"**DAY {self.nth} - {self.date.strftime('%d-%m-%Y')} - SOLUTIONS**"
    msg["questions"] = []
    for x in self.ques:
      soln_msg = f"**{x.nth}) {x.level}:** <{x.link}\nSoln: {x.soln}>"
      msg["questions"].append(soln_msg)
    return msg

class DailyQuestions_All:

  def __init__(self):
    self.days = {}

  def add_day(self, new_day: DailyQuestions_Day):
    self.days[new_day.nth] = new_day
    self.days[new_day.date] = new_day

class DailyQuestions_Details:
  def __init__(self, dq_details_str: str):
    self.time = csf.str_in_bw(dq_details_str, "<time>", "</time>")
    self.ques_channel = int(csf.str_in_bw(dq_details_str, "<dq_ques_channel>", "</dq_ques_channel>"))
    self.soln_channel = int(csf.str_in_bw(dq_details_str, "<dq_soln_channel>", "</dq_soln_channel>"))
    self.announcement_channel = int(csf.str_in_bw(dq_details_str, "<dq_announcement_channel>", "</dq_announcement_channel>"))
    self.admin_roles = []
    temp_str = csf.str_in_bw(dq_details_str, "<dq_admin_roles>", "</dq_admin_roles>")
    while "</a>" in temp_str:
      self.admin_roles.append(int(csf.str_in_bw(temp_str, "<a>", "</a>")))
      temp_str = csf.str_after(temp_str, "</a>")
    self.admin_users = []
    temp_str = csf.str_in_bw(dq_details_str, "<dq_admin_users>", "</dq_admin_users>")
    while "</a>" in temp_str:
      self.admin_users.append(int(csf.str_in_bw(temp_str, "<a>", "</a>")))
      temp_str = csf.str_after(temp_str, "</a>")
  
  def to_str(self):
    string = "<time>" + self.time + "</time>\n"
    string += "<dq_ques_channel>" + str(self.ques_channel) + "</dq_ques_channel>\n"
    string += "<dq_soln_channel>" + str(self.soln_channel) + "</dq_soln_channel>\n"
    string += "<dq_announcement_channel>" + str(self.announcement_channel) + "</dq_announcement_channel>\n"
    string += "<dq_admin_roles>"
    for x in self.admin_roles:
      string += "<a>" + str(x) + "</a>"
    string += "</dq_admin_roles>\n"
    string += "<dq_admin_users>"
    for x in self.admin_users:
      string += "<a>" + str(x) + "</a>"
    string += "</dq_admin_users>\n"
    return string

class DailyQuestions_File:
  def __init__(self):
    self.file_path = "/home/runner/Shot/Data/daily_questions.data"
    self.file_data = cr.encrypted_file_read(self.file_path)
    dq_details_str = csf.str_in_bw(self.file_data, "<dq_details>", "</dq_details>")
    self.details = DailyQuestions_Details(dq_details_str)
  
  def write(self):
    cr.encrypted_file_write(self.file_path, self.file_data)

  def write_details(self):
    dq_details_str =  "<dq_details>" + self.details.to_str() + "</dq_details>"
    dq_old_details_str = csf.str_in_bw(self.file_data, "<dq_details>", "</dq_details>", 1)
    self.file_data = csf.str_replace(self.file_data, dq_old_details_str, dq_details_str, 1)
    self.write()
  
  def get_questions(self):
    DailyQuestions = DailyQuestions_All()
    data = csf.str_in_bw(self.file_data, "<start>", "<end>")
    while "</dq>" in data:
      curr_day = DailyQuestions_Day(csf.str_in_bw(data, "<dq>", "</dq>"))
      data = csf.str_after(data, "</dq>")
      DailyQuestions.add_day(curr_day)
    return DailyQuestions

  def get_day_list(self):
    DailyQuestions = self.get_questions()
    DailyQuestions_DayList = []
    for x in DailyQuestions.days:
      if isinstance(x, int):
        DailyQuestions_DayList.append([x, DailyQuestions.days[x].date])
    return DailyQuestions_DayList
  
  def remove_day(self, day):
    DailyQuestions = self.get_questions()
    if day not in DailyQuestions.days:
      return False
    data = csf.str_in_bw(self.file_data, "<start>", "<end>")
    day = DailyQuestions.days[day]
    while "</dq>" in data:
      curr_day_str = csf.str_in_bw(data, "<dq>", "</dq>", 1)
      data = csf.str_after(data, "</dq>")
      if "<nth>" + str(day.nth) + "</nth>" in curr_day_str:
        self.file_data = csf.str_replace(self.file_data, curr_day_str, count = 1)
        break
    self.write()
    return day
  
  def write_new_day(self, curr_day: DailyQuestions_Day):
    day_exists = self.day_exists(curr_day)
    if day_exists:
      return False
    day_str = curr_day.to_str()
    self.file_data = csf.str_replace(self.file_data, "<end>", day_str + "<end>", 1)
    self.write()
    return True

  def day_exists(self, curr_day):
    DailyQuestions = self.get_questions()
    if isinstance(curr_day, str) and curr_day.isdigit():
      curr_day = int(curr_day)
    if isinstance(curr_day, datetime) or isinstance(curr_day, int):
      if curr_day in DailyQuestions.days:
        return DailyQuestions.days[curr_day]
      return False
    elif isinstance(curr_day, str):
      curr_day = crf.check_valid_date(curr_day)
      if not curr_day or curr_day not in DailyQuestions.days:
        return False
      return DailyQuestions.days[curr_day]
    elif isinstance(curr_day, DailyQuestions_Day):
      same_nth = [False]
      same_date = [False]
      if curr_day.nth in DailyQuestions.days:
        same_nth = [True, curr_day.nth, DailyQuestions.days[curr_day.nth].date]
      if curr_day.date in DailyQuestions.days:
        same_date = [True, DailyQuestions.days[curr_day.date].nth, curr_day.date]
      if not (same_nth[0] or same_date[0]):
        return False
      return {"same_nth": same_nth, "same_date": same_date}

def get_dq_time():
  file_path = "/home/runner/Shot/Data/daily_questions.data"
  time = cr.encrypted_file_read(file_path)
  time = csf.str_in_bw(time, "<time>", "</time>")
  time = datetime(1, 1, 1, int(csf.str_before(time, ":")), int(csf.str_after(time, ":")))
  return time

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









