from datetime import datetime, timedelta
import os
import glob
from Data import emojis
import custom_string_functions as csf
import custom_random_functions as crf
from DailyQuestions import daily_question_errors as dqe
import config_reader as cr

dq_folder_path = "Daily Questions\\"
dq_days_folder_path = dq_folder_path + "Days\\"

class DailyQuestions_Question:

  def __init__(self, curr_ques_str: str, day_file_path: str = "not passed"):
    self.nth = int(cr.config_reader(curr_ques_str, "q_n"))
    self.lvl = cr.config_reader(curr_ques_str, "q_lvl")
    self.lvl = get_level(self.lvl)
    self.link = cr.config_reader(curr_ques_str, "q_link")
    self.note = cr.config_reader(curr_ques_str, "q_note")
    self.soln = cr.config_reader(curr_ques_str, "q_soln")
    self.pts = cr.config_reader(curr_ques_str, "q_pts")
    if not self.nth or not self.link:
      raise dqe.DailyQuestions_Question_InvalidQuestion(day_file_path)
  
  def to_str(self):
    string = ""
    string += "<q_n>" + str(self.nth)  + "</q_n>\n"
    string += "<q_lvl>" + self.lvl  + "</q_lvl>\n"
    string += "<q_link>" + self.link  + "</q_link>\n"
    string += "<q_note>" + self.note  + "</q_note>\n"
    string += "<q_soln>" + self.soln  + "</q_soln>\n"
    string += "<q_pts>" + self.pts  + "</q_pts>"
    return string

class DailyQuestions_Day:
  def __init__(self, curr_day: str, from_str: bool = False):
    if from_str:
      self.load_from_str(curr_day)
    else:
      self.file_path = curr_day
      self.load_from_file()
    
  def load_from_file(self):
    if not os.path.isfile(self.file_path):
      raise dqe.DailyQuestions_Day_FileNotFound(self.file_path)
    curr_day_str = cr.encrypted_file_read(self.file_path)
    self.load_from_str(curr_day_str)
    self.validate_file_name()
  
  def load_from_str(self, curr_day_str: str):
    self.start_date = cr.config_reader(curr_day_str, "d_date")
    self.start_date = crf.check_valid_date(self.start_date, True)
    self.nth = int(cr.config_reader(curr_day_str, "d_nth"))
    self.duration = int(cr.config_reader(curr_day_str, "d_duration"))
    if not (self.start_date and self.nth and self.duration):
      raise dqe.DailyQuestions_Day_InvalidFileData
    if not hasattr(self, "file_path"):
      self.file_path = f"{dq_days_folder_path}\\[{self.start_date.strftime('%Y-%m-%d')}] {{{self.nth}}} ({self.duration}).data"
    self.note = cr.config_reader(curr_day_str, "d_note")
    self.ques = {}
    while "</q>" in curr_day_str:
      curr_ques_str = csf.in_bw(curr_day_str, "<q>", "</q>")
      curr_day_str = csf.after(curr_day_str, "</q>")
      curr_ques = DailyQuestions_Question(curr_ques_str, self.file_path)
      self.ques[curr_ques.nth] = curr_ques
    if not len(self.ques):
      raise dqe.DailyQuestions_Day_NoQuestions(self.file_path)
  
  def validate_file_name(self):
    file_name = self.file_path[csf.last_occurance(self.file_path, "\\") + 1:]
    file_name = file_name[0 : csf.last_occurance(file_name, ".")]
    start_date = csf.in_bw(file_name, "[", "]")
    start_date = crf.check_valid_date(self.start_date, True)
    nth = int(csf.in_bw(file_name, "{", "}"))
    duration = int(csf.in_bw(file_name, "(", ")"))
    if not (file_name and start_date and nth and duration) or (self.start_date != start_date) or (self.nth != nth) or (self.duration != duration):
      raise dqe.DailyQuestions_Day_InvalidFileName(self.file_path)
  
  def write(self):
    cr.encrypted_file_write(self.file_path, self.to_str)
  
  def to_str(self):
    string = ""
    string += "<d_date>" + self.start_date.strftime('%Y-%m-%d') + "</d_date>\n"
    string += "<d_nth>" + str(self.nth) + "</d_nth>\n"
    string += "<d_duration>" + str(self.duration) + "</d_duration>\n"
    string += "<d_note>" + str(self.note) + "</d_note>"
    for x in self.ques:
      string += "\n<q>\n" + x.to_str() + "\n</q>"
    return string

  def to_file_name(self):
    return f"[{self.start_date.strftime('%Y-%m-%d')}] {{{self.nth}}} ({self.duration}).data"
  
  def to_announce_ques(self):
    msg = dict()
    msg["title"] = f"**DAILY PROBLEMS (DAY{self.nth}{'' if (self.duration == 1) else f' - {self.nth + self.duration - 1}'}) - {self.date.strftime('%d-%m-%Y')}**"
    msg["questions"] = list()
    for x in self.ques:
      ques_msg = f"**Question {x.nth}:**"
      if x.lvl:
        ques_msg += f"\n**Level:** {x.lvl}"
      if x.pts:
        ques_msg += f"\n**Points:** {x.pts}"
      ques_msg += f"\n**Link:** <{x.link}>"
      if x.note:
        ques_msg += f"\n**Note:** {x.note}"
      msg["questions"].append(ques_msg)
    return msg

  def to_announce_soln(self):
    msg = dict()
    msg["title"] = f"**DAY{self.nth}{'' if (self.duration == 1) else f' - {self.nth + self.duration - 1}'} - {self.date.strftime('%d-%m-%Y')} - SOLUTIONS**"
    msg["questions"] = list()
    for x in self.ques:
      soln_msg = f"**Question {x.nth}:**"
      if x.lvl:
        soln_msg += f"\n**Level:** {x.lvl}"
      soln_msg += f"\n**Link:** <{x.link}>"
      if "</img>" not in x.soln:
        soln_msg += f"\n**Soln** {x.soln}"
        msg["questions"].append([soln_msg])
      else:
        soln_msg += f"\n**Soln** {csf.before(x.soln, '<img>')}"
        soln_list = []
        soln_list.append(soln_msg)
        soln = x.soln
        soln = csf.after(soln, "<img>")
        while "</img>" in soln:
          img = csf.before(soln, "</img>")
          soln = csf.after(soln, "</img>")
          soln_list.append(img)
          if "<img>" not in soln:
            break
          soln_msg = csf.before(soln, "<img>")
          soln = csf.after(soln, "<img>")
          if soln_msg.strip("\n\r\t "):
            soln_list.append(soln_msg)
        if soln.strip("\n\r\t "):
          soln_list.append(soln)
        msg["questions"].append(soln_list)
    return msg
  
class DailyQuestions_Details:
  def __init__(self):
    self.file_path = dq_days_folder_path + "details.data"
    file_data = cr.encrypted_file_read(self.file_path)
    self.time = cr.config_reader(file_data, "time")
    self.time = crf.check_valid_time(self.time)
    self.ques_chnl = cr.config_reader(file_data, "ques_chnl")
    self.soln_chnl = cr.config_reader(file_data, "soln_chnl")
    self.announcement_chnl = cr.config_reader(file_data, "announcement_chnl")
    self.admin_chnl = cr.config_reader(file_data, "admin_chnl")
    self.admin_roles = cr.config_reader(file_data, "admin_roles")
    self.admin_roles = [int(x) for x in self.admin_roles.split(";")]
    self.admin_users = cr.config_reader(file_data, "admin_users")
    self.admin_users = [int(x) for x in self.admin_users.split(";")]
    self.validate()
    
  def to_str(self):
    string = ""
    string += "<time>" + self.time.strftime('%H:%M') + "</time>\n"
    string += "<ques_chnl>" + str(self.ques_chnl) + "</ques_chnl>\n"
    string += "<soln_chnl>" + str(self.soln_chnl) + "</ques_chnl>\n"
    string += "<announcement_chnl>" + str(self.announcement_chnl) + "</ques_chnl>\n"
    string += "<admin_chnl>" + str(self.admin_chnl) + "</ques_chnl>\n"
    string += "<admin_roles>"
    for x in self.admin_roles:
      string += str(x) + ";"
    string = string[0 : len(string) - 1]
    string += "</admin_roles>\n"
    string += "<admin_users>"
    for x in self.admin_users:
      string += str(x) + ";"
    string = string[0 : len(string) - 1]
    string += "</admin_users>"
    return string
  
  def validate(self):
    if not (self.time and self.ques_chnl and self.soln_chnl and self.announcement_chnl and self.admin_chnl and (self.admin_roles or self.admin_users)):
      raise dqe.DailyQuestions_Details_InvalidData()
  
  def write(self):
    self.validate()
    cr.encrypted_file_write(self.file_path, self.to_str)

class DailyQuestions:
  def __init__(self):
    self.folder_path = dq_folder_path
    self.days_folder = dq_days_folder_path

  def get_day_list(self):
    day_list = [map()]
    for filename in glob.glob("[????-??-??] {*} {*}.data", self.days_folder):
      curr_day = {}
      curr_day["start"] = crf.check_valid_date(csf.in_bw(filename, "[", "]"))
      curr_day["nth"] = int(csf.in_bw(filename, "{", "}"))
      curr_day["duration"] = int(csf.in_bw(filename, "(", ")"))
      curr_day["filename"] = filename
      for i in range(0, curr_day["duration"]):
        day_list[0][curr_day["start"] + timedelta(days = i)] = filename
        day_list[0][curr_day["nth"] + i] = filename
      day_list.append(curr_day)
    return day_list
  
  def check_existing_day(self, curr_day: DailyQuestions_Day):
    day_list = self.get_day_list()
    day_span = []
    for i in range(0, curr_day.duration):
      day_span.append(curr_day.start_date + timedelta(days = i))
      day_span.append(curr_day.nth + i)
    clashing_days = set()
    for i in day_span:
      if i in day_list[0]:
        clashing_days.add(day_list[0][i])
    return clashing_days

  def remove_day(self, curr_day: datetime or int):
    day_list = self.get_day_list()
    if curr_day not in day_list[0]:
      raise dqe.DailyQuestions_Day_FileNotFound(curr_day)
    curr_day_path = self.days_folder + day_list[0][curr_day]
    if not os.path.isfile(curr_day):
      raise dqe.DailyQuestions_Day_FileNotFound(curr_day)
    curr_day = DailyQuestions_Day(curr_day_path)
    curr_day_raw = cr.encrypted_file_read(curr_day_path)
    os.remove(curr_day_path)
    return {"day": curr_day, "raw": curr_day_raw}
  
  def add_day(self, curr_day_str: str):
    curr_day = DailyQuestions_Day(curr_day_str, True)
    clashing_days = self.check_existing_day(curr_day)
    if len(clashing_days):
      raise dqe.DailyQuestions_AddDay_Clashing()
    curr_day.write()
    return curr_day

  def get_day(self, curr_day: datetime or int):
    day_list = self.get_day_list()
    if curr_day not in day_list[0]:
      raise dqe.DailyQuestions_Day_FileNotFound(curr_day)
    curr_day_path = self.days_folder + day_list[0][curr_day]
    return DailyQuestions_Day(curr_day_path)

  def get_day_raw(self, curr_day: datetime or int):
    day_list = self.get_day_list()
    if curr_day not in day_list[0]:
      raise dqe.DailyQuestions_Day_FileNotFound(curr_day)
    curr_day_path = self.days_folder + day_list[0][curr_day]
    return cr.encrypted_file_read(curr_day_path)
    
    
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
