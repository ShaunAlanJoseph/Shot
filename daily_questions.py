from datetime import datetime
import custom_string_functions as csf
import custom_random_functions as crf
from Data import emojis
import config_reader as cr

daily_questions_file_path = "/home/runner/Shot/Data/Daily Questions/daily_questions.data"

class DailyQuestions_Question:

  def __init__(self, nth: int, level, link, note, soln):
    self.nth = nth
    self.level = get_level(level)
    self.link = link
    self.note = note
    self.soln = soln
  
  def __init__(self, curr_ques_str: str):
    self.nth = int(csf.str_in_bw(curr_ques_str, "<q_n>", "</q_n>"))
    self.level = csf.str_in_bw(curr_ques_str, "<q_lvl>", "</q_lvl>")
    self.level = get_level(self.level)
    self.link = csf.str_in_bw(curr_ques_str, "<q_link>", "</q_link>")
    self.note = csf.str_in_bw(curr_ques_str, "<q_note>", "</q_note>")
    self.soln = csf.str_in_bw(curr_ques_str, "<q_soln>", "</q_soln>")

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
      day_str += "<q_n>" + str(curr_ques.nth) + "</q_n>\n"
      day_str += "<q_lvl>" + curr_ques.level + "</q_lvl>\n"
      day_str += "<q_link>" + curr_ques.link + "</q_link>\n"
      day_str += "<q_note>" + curr_ques.note + "</q_note>\n"
      day_str += "<q_soln>" + curr_ques.soln + "</q_soln>\n"
      day_str += "</q>\n"
    day_str += "</dq>"
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
        ques_msg += f"\nNote: {x.note}"
      msg["questions"].append(ques_msg)
    return msg
  
  def to_announce_soln(self):
    msg = {}
    msg["title"] = f"**DAY {self.nth} - {self.date.strftime('%d-%m-%Y')} - SOLUTIONS**"
    msg["questions"] = []
    for x in self.ques:
      if "</img>" not in x.soln:
        soln_msg = f"**{x.nth}) {x.level}:** <{x.link}>\n**Soln:** {x.soln}"
        msg["questions"].append([soln_msg])
      else:
        soln = x.soln
        soln_list = []
        soln_msg = f"**{x.nth}) {x.level}:** <{x.link}>\n**Soln:** {csf.str_before(soln, '<img>')}"
        soln = csf.str_after(soln, "<img>")
        soln_list.append(soln_msg)
        while "</img>" in soln:
          img = csf.str_before(soln, "</img>")
          soln = csf.str_after(soln, "</img>")
          soln_list.append(img)
          if "<img>" not in soln:
            break
          soln_msg = csf.str_before(soln, "<img>")
          soln = csf.str_after(soln, "<img>")
          if soln_msg.strip("\n\r\t "):
            soln_list.append(soln_msg)
        if soln.strip("\n\r\t "):
          soln_list.append(soln)
        msg["questions"].append(soln_list)
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
    self.ques_chnl = int(csf.str_in_bw(dq_details_str, "<dq_ques_chnl>", "</dq_ques_chnl>"))
    self.soln_chnl = int(csf.str_in_bw(dq_details_str, "<dq_soln_chnl>", "</dq_soln_chnl>"))
    self.announcement_chnl = int(csf.str_in_bw(dq_details_str, "<dq_announcement_chnl>", "</dq_announcement_chnl>"))
    self.admin_chnl = int(csf.str_in_bw(dq_details_str, "<dq_admin_chnl>", "</dq_admin_chnl>"))
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
    string = "<dq_details>\n"
    string += "<time>" + self.time + "</time>\n"
    string += "<dq_ques_chnl>" + str(self.ques_chnl) + "</dq_ques_chnl>\n"
    string += "<dq_soln_chnl>" + str(self.soln_chnl) + "</dq_soln_chnl>\n"
    string += "<dq_announcement_chnl>" + str(self.announcement_chnl) + "</dq_announcement_chnl>\n"
    string += "<dq_admin_chnl>" + str(self.admin_chnl) + "</dq_admin_chnl>\n"
    string += "<dq_admin_roles>"
    for x in self.admin_roles:
      string += "<a>" + str(x) + "</a>"
    string += "</dq_admin_roles>\n"
    string += "<dq_admin_users>"
    for x in self.admin_users:
      string += "<a>" + str(x) + "</a>"
    string += "</dq_admin_users>\n"
    string += "</dq_details>"
    return string

class DailyQuestions_File:
  def __init__(self):
    self.file_path = daily_questions_file_path
    self.file_data = cr.encrypted_file_read(self.file_path)
    dq_details_str = csf.str_in_bw(self.file_data, "<dq_details>", "</dq_details>")
    self.details = DailyQuestions_Details(dq_details_str)
  
  def write(self):
    cr.encrypted_file_write(self.file_path, self.file_data)

  def write_details(self):
    dq_details_str =  self.details.to_str()
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
  
  def remove_day(self, curr_day):
    DailyQuestions = self.get_questions()
    if curr_day not in DailyQuestions.days:
      return False
    data = csf.str_in_bw(self.file_data, "<start>", "<end>")
    curr_day = DailyQuestions.days[curr_day]
    curr_day_str = ""
    while "</dq>" in data:
      curr_day_str = csf.str_in_bw(data, "<dq>", "</dq>", 1)
      data = csf.str_after(data, "</dq>")
      if "<nth>" + str(curr_day.nth) + "</nth>" in curr_day_str:
        self.file_data = csf.str_replace(self.file_data, curr_day_str, count = 1)
        break
    self.write()
    return {"day": curr_day, "raw": curr_day_str} # So that the exact data removed can be printed.

  def replace_day(self, old_day, new_day: DailyQuestions_Day):
    DailyQuestions = self.get_questions()
    if old_day not in DailyQuestions.days:
      print(f"Old day corresponding to: {old_day} was not found.")
      return False
    old_day = DailyQuestions.days[old_day]
    del DailyQuestions.days[old_day.nth]
    del DailyQuestions.days[old_day.date]
    if new_day.nth in DailyQuestions.days or new_day.date in DailyQuestions.days:
      print(f"New day is clashing with a day other than the date to be replaced. nth: {new_day.nth} date: {new_day.date.strftime('%d-%m-%Y')}")
      return False
    data = csf.str_in_bw(self.file_data, "<start>", "<end>")
    curr_day_str = ""
    while "</dq>" in data:
      curr_day_str = csf.str_in_bw(data, "<dq>", "</dq>", 1)
      data = csf.str_after(data, "</dq>")
      if "<nth>" + str(old_day.nth) + "</nth>" in curr_day_str:
        self.file_data = csf.str_replace(self.file_data, curr_day_str, new_day.to_str(), 1)
        break
    self.write()
    return {"day": old_day, "raw": curr_day_str} # So that the exact data replaced can be printed.
  
  def write_new_day(self, curr_day: DailyQuestions_Day):
    day_exists = self.day_exists(curr_day)
    if day_exists:
      return False
    day_str = curr_day.to_str()
    self.file_data = csf.str_replace(self.file_data, "<end>", day_str + "\n<end>", 1)
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
  file_path = daily_questions_file_path
  time = cr.encrypted_file_read(file_path)
  time = csf.str_in_bw(time, "<time>", "</time>")
  time = datetime(1, 1, 1, int(csf.str_before(time, ":")), int(csf.str_after(time, ":")))
  return time

def get_level(level):
  if level in ["Cakewalk", "Easy", "Medium", "Hard", "Giveup", "Cakewalk-Easy", "Easy-Medium", "Medium-Hard", "Hard-Giveup"]:
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
