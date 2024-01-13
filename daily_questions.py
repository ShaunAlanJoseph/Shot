from datetime import datetime, timedelta
import os
import glob
from Data import emojis
import custom_string_functions as csf
import custom_random_functions as crf
from DailyQuestions import daily_question_errors as dqe
import config_reader as cr
import traceback
import pastebin_reader as pr

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
    self.pbm = pr.PasteBin_main()
    if from_str:
      self.load_from_str(curr_day)
    else:
      self.file_name = curr_day
      self.load_from_file()

  def load_from_file(self):
    if self.file_name not in self.pbm.main["dq"]["days"]:
      raise dqe.DailyQuestions_Day_FileNotFound(self.file_name)
    curr_day_str = self.pbm.get_dq_day(self.file_name)
    self.load_from_str(curr_day_str)
    self.validate_file_name()

  def load_from_str(self, curr_day_str: str):
    self.start_date = cr.config_reader(curr_day_str, "d_date")
    self.start_date = crf.check_valid_date(self.start_date, True)
    self.nth = int(cr.config_reader(curr_day_str, "d_nth"))
    self.duration = int(cr.config_reader(curr_day_str, "d_duration"))
    if not (self.start_date and self.nth and self.duration):
      raise dqe.DailyQuestions_Day_InvalidFileData(self.file_name if hasattr(self, "file_name") else "loaded from str")
    if not hasattr(self, "file_name"):
      self.file_name = f"[{self.start_date.strftime('%Y-%m-%d')}] {{{self.nth}}} ({self.duration})"
    self.note = cr.config_reader(curr_day_str, "d_note")
    self.ques = dict()
    while "</q>" in curr_day_str:
      curr_ques_str = csf.in_bw(curr_day_str, "<q>", "</q>")
      curr_day_str = csf.after(curr_day_str, "</q>")
      curr_ques = DailyQuestions_Question(curr_ques_str, self.file_name)
      self.ques[curr_ques.nth] = curr_ques
    if not len(self.ques):
      raise dqe.DailyQuestions_Day_NoQuestions(self.file_name)

  def validate_file_name(self):
    start_date = csf.in_bw(self.file_name, "[", "]")
    start_date = crf.check_valid_date(self.start_date, True)
    nth = int(csf.in_bw(self.file_name, "{", "}"))
    duration = int(csf.in_bw(self.file_name, "(", ")"))
    if not (self.file_name and start_date and nth and duration) or (self.start_date != start_date) or (self.nth != nth) or (self.duration != duration):
      raise dqe.DailyQuestions_Day_InvalidFileName(self.file_name)

  def write(self):
    self.pbm.add_dq_day(self.file_name, self.to_str())

  def to_str(self):
    string = ""
    string += "<d_date>" + self.start_date.strftime('%Y-%m-%d') + "</d_date>\n"
    string += "<d_nth>" + str(self.nth) + "</d_nth>\n"
    string += "<d_duration>" + str(self.duration) + "</d_duration>\n"
    string += "<d_note>" + str(self.note) + "</d_note>"
    for x in self.ques:
      string += "\n<q>\n" + self.ques[x].to_str() + "\n</q>"
    return string

  def to_file_name(self):
    return f"[{self.start_date.strftime('%Y-%m-%d')}] {{{self.nth}}} ({self.duration})"

  def to_announce_ques(self):
    msg = dict()
    msg["title"] = f"**DAILY PROBLEMS (DAY{self.nth}{'' if (self.duration == 1) else f' - {self.nth + self.duration - 1}'}) - {self.start_date.strftime('%d-%m-%Y')}**"
    msg["questions"] = list()
    for x in self.ques:
      ques_msg = f"**Question {self.ques[x].nth}:**"
      if self.ques[x].lvl:
        ques_msg += f"\n**Level:** {self.ques[x].lvl}"
      if self.ques[x].pts:
        ques_msg += f"\n**Points:** {self.ques[x].pts}"
      ques_msg += f"\n**Link:** <{self.ques[x].link}>"
      if self.ques[x].note:
        ques_msg += f"\n**Note:** {self.ques[x].note}"
      msg["questions"].append(ques_msg)
    return msg

  def to_announce_soln(self):
    msg = dict()
    msg["title"] = f"**DAY{self.nth}{'' if (self.duration == 1) else f' - {self.nth + self.duration - 1}'} - {self.start_date.strftime('%d-%m-%Y')} - SOLUTIONS**"
    msg["questions"] = list()
    for x in self.ques:
      soln_msg = f"**Question {self.ques[x].nth}:**"
      if self.ques[x].lvl:
        soln_msg += f"\n**Level:** {self.ques[x].lvl}"
      soln_msg += f"\n**Link:** <{self.ques[x].link}>"
      if "</img>" not in self.ques[x].soln:
        soln_msg += f"\n**Soln:**\n{self.ques[x].soln}"
        msg["questions"].append([soln_msg])
      else:
        soln_msg += f"\n**Soln:**\n{csf.before(self.ques[x].soln, '<img>')}"
        soln_list = []
        soln_list.append(soln_msg)
        soln = self.ques[x].soln
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

class DailyQuestions_Settings:
  def __init__(self, settings_str = ""):
    if not settings_str:
      self.pbm = pr.PasteBin_main()
      settings_str = self.pbm.get_file(self.pbm.main["days"]["settings"])
    self.time = cr.config_reader(settings_str, "time")
    self.time = crf.check_valid_time(self.time)
    self.ques_chnl = cr.config_reader(settings_str, "ques_chnl")
    self.soln_chnl = cr.config_reader(settings_str, "soln_chnl")
    self.announcement_chnl = cr.config_reader(settings_str, "announcement_chnl")
    self.admin_chnl = cr.config_reader(settings_str, "admin_chnl")
    self.admin_roles = cr.config_reader(settings_str, "admin_roles")
    self.admin_roles = [int(x) for x in self.admin_roles.split(";") if x]
    self.admin_users = cr.config_reader(settings_str, "admin_users")
    self.admin_users = [int(x) for x in self.admin_users.split(";") if x]
    self.validate()

  def to_str(self):
    string = ""
    string += "<time>" + self.time.strftime('%H:%M') + "</time>\n"
    string += "<ques_chnl>" + str(self.ques_chnl) + "</ques_chnl>\n"
    string += "<soln_chnl>" + str(self.soln_chnl) + "</soln_chnl>\n"
    string += "<announcement_chnl>" + str(self.announcement_chnl) + "</announcement_chnl>\n"
    string += "<admin_chnl>" + str(self.admin_chnl) + "</admin_chnl>\n"
    string += "<admin_roles>"
    for x in self.admin_roles:
      string += str(x) + ";"
    if len(self.admin_roles):
      string = string[0 : len(string) - 1]
    string += "</admin_roles>\n"
    string += "<admin_users>"
    for x in self.admin_users:
      string += str(x) + ";"
    string = string[0 : len(string) - 1]
    string += "</admin_users>\n"
    string += "# Use ; as the separator between admin_roles and admin_users."
    return string

  def validate(self):
    if not (self.time and self.ques_chnl and self.soln_chnl and self.announcement_chnl and self.admin_chnl and (self.admin_roles or self.admin_users)):
      raise dqe.DailyQuestions_Settings_InvalidData()

  def write(self):
    self.validate()
    self.pbm.edit_dq_file("settings", self.to_str())

class DailyQuestions_QuestionTracker:
  def __init__(self):
    self.pbm = pr.PasteBin_main()
    self.read_questions()
  
  def read_questions(self):
    file_data = self.pbm.get_file(self.pbm.main["dq"]["ques_dump"])
    self.ques = dict()
    while "<\q>" in file_data:
      curr_ques = cr.config_reader(file_data, "q")
      file_data = csf.after(file_data, "</q>")
      self.ques[cr.config_reader(curr_ques, "a")] = {"day": cr.config_reader(curr_ques, "d"), "pf": cr.config_reader(curr_ques, "pf")}
  
  def format_ques(self, ques_str: str, day: int = 0):
    ques = {"day": day}
    ques_str = csf.after(ques_str, "https://")
    ques_str.rstrip("/")
    
    if "codeforces.com" in ques_str:
      ques["pf"] = "CF"
      ques["ques"] = "-" + ques_str[csf.last_occurance(ques_str, "/") + 1:]
      while "/" in ques_str:
        if csf.before(ques_str, "/").isdigit():
          ques["ques"] = csf.before(ques_str, "/") + ques["ques"]
          break
        ques_str = csf.after(ques_str, "/")
      
    elif "codechef.com" in ques_str:
      ques["pf"] = "CC"
      ques["ques"] = ques_str[csf.last_occurance(ques_str, "/") + 1:]
    
    elif "cses.fi" in ques_str:
      ques["pf"] = "CS"
      ques["ques"] = ques_str[csf.last_occurance(ques_str, "/") + 1:]
      
    else:
      ques["pf"] = "OT"
      ques["ques"] = ques_str
      
    return ques
  
  def check_unique_ques(self, ques_str: str, day: int = 0):
    curr_ques = self.format_ques(ques_str, day)
    if curr_ques["ques"] in self.ques:
      return False
    return curr_ques
  
  def add_day_ques(self, curr_day: DailyQuestions_Day):
    for v in curr_day.ques.values():
      self.add_ques(v.link, curr_day.nth)
  
  def remove_day_ques(self, curr_day: DailyQuestions_Day):
    for v in curr_day.ques.values():
      self.remove_ques(v.link)
  
  def add_ques(self, ques_str: str, day: int):
    curr_ques = self.check_unique_ques(ques_str, day)
    if not curr_ques:
      raise dqe.DailyQuestions_QuestionTracker_Clashing(ques_str)
    
    self.ques[curr_ques["ques"]] = {"day": curr_ques["day"], "pf": curr_ques["pf"]}
    self.write()
  
  def remove_ques(self, ques_str: str):
    curr_ques = self.format_ques(ques_str)
    
    if curr_ques["ques"] not in self.ques:
      raise dqe.DailyQuestions_QuestionTracker_QuesNotFound(ques_str)
    
    self.ques.pop(curr_ques["ques"])
    self.write()
  
  def to_str(self):
    string = ""
    for q, v in self.ques.items():
      string += "<q>"
      string += "<a>" + q + "</a>"
      string += "<d>" + str(v["day"]) + "</d>"
      string += "<pf>" + v["pf"] + "</pf>"
      string += "</q>\n"
    return string

  def write(self):
    self.pbm.edit_dq_file("ques_dump", self.to_str())
  
  def get_ques_from_files(self):
    try:
      for filename in self.pbm.main["dq"]["days"].keys():
        curr_day = DailyQuestions_Day(filename)
        for v in curr_day.ques.values():
          self.add_ques(v.link, curr_day.nth)
    except Exception as ex:
      traceback.print_exc()

class DailyQuestions:
  def __init__(self):
    self.pbm = pr.PasteBin_main()

  def get_day_list(self):
    day_list = []
    day_dict = dict()
    for filename in self.pbm.main["dq"]["days"]:
      curr_day = {}
      curr_day["start"] = crf.check_valid_date(csf.in_bw(filename, "[", "]"), True)
      curr_day["nth"] = int(csf.in_bw(filename, "{", "}"))
      curr_day["duration"] = int(csf.in_bw(filename, "(", ")"))
      curr_day["filename"] = filename
      for i in range(0, curr_day["duration"]):
        day_dict[curr_day["start"] + timedelta(days = i)] = filename
        day_dict[curr_day["nth"] + i] = filename
      day_list.append(curr_day)
    return [day_dict] + sorted(day_list, key=lambda day: day["nth"])

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
    curr_day_file_name = day_list[0][curr_day]
    curr_day = DailyQuestions_Day(curr_day_file_name)
    curr_day_raw = self.pbm.get_dq_day(curr_day_file_name)
    ques_tracker = DailyQuestions_QuestionTracker()
    ques_tracker.remove_day_ques(curr_day)
    self.pbm.remove_dq_day(curr_day_file_name)
    
    return {"day": curr_day, "raw": curr_day_raw}

  def add_day(self, curr_day_str: str):
    curr_day = DailyQuestions_Day(curr_day_str, True)
    clashing_days = self.check_existing_day(curr_day)
    if len(clashing_days):
      raise dqe.DailyQuestions_AddDay_Clashing()
    ques_tracker = DailyQuestions_QuestionTracker()
    ques_tracker.add_day_ques(curr_day)
    curr_day.write()
    return curr_day

  def get_day(self, curr_day: datetime or int):
    day_list = self.get_day_list()
    if curr_day not in day_list[0]:
      raise dqe.DailyQuestions_Day_FileNotFound(curr_day)
    curr_day_file_name = day_list[0][curr_day]
    return DailyQuestions_Day(curr_day_file_name)

  def get_day_raw(self, curr_day: datetime or int):
    day_list = self.get_day_list()
    if curr_day not in day_list[0]:
      raise dqe.DailyQuestions_Day_FileNotFound(curr_day)
    curr_day_file_name = day_list[0][curr_day]
    return cr.encrypted_file_read(curr_day_file_name)


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