import requests
import os
import custom_string_functions as csf

class PasteBin_NoDevKey(Exception):
  def __init__(self):
    self.message = f"Developer key is required to use the PasteBin API!"
    super().__init__(self.message)

class PasteBin_NoRequestData(Exception):
  def __init__(self):
    self.message = f"No data was given for the request."
    super().__init__(self.message)

class PasteBin_BadAPIRequest(Exception):
  def __init__(self, bad_response):
    self.message = f"{bad_response}"
    super().__init__(self.message)

class PasteBin_UserKeyRequired(Exception):
  def __init__(self, method):
    self.message = f"api_user_key is required for: {method}"
    super().__init__(self.message)

class PasteBin_main_DayAlreadyExists(Exception):
  def __init__(self, day):
    self.message = f"Day already exists: {day}"
    super().__init__(self.message)

class PasteBin_main_DayNotFound(Exception):
  def __init__(self, day):
    self.message = f"Day not found: {day}"
    super().__init__(self.message)

class PasteBin:
  def __init__(self, api_dev_key: str = None, api_user_name: str = None, api_user_password: str = None):
    if (api_dev_key == None):
      api_dev_key = os.environ["PASTEBIN_API_DEV_KEY"]
    if (api_user_name == None):
      api_user_name = os.environ["PASTEBIN_API_USER_NAME"]
    if (api_user_password == None):
      api_user_password  = os.environ["PASTEBIN_API_USER_PASSWORD"]

    if not api_dev_key:
      raise PasteBin_NoDevKey()
    
    self.api_dev_key = api_dev_key
    self.api_user_name = api_user_name
    self.api_user_password = api_user_password

    self.load_urls()
  
    if self.api_user_name and self.api_user_password:
      self.api_user_key = self.get_user_key()
  
  def load_urls(self):
    self.api_post_url = "https://pastebin.com/api/api_post.php"
    self.api_login_url = "https://pastebin.com/api/api_login.php"
    self.api_raw_url = "https://pastebin.com/api/api_raw.php"
  
  def get_user_key(self):
    self.data = {"api_dev_key": self.api_dev_key, "api_user_name": self.api_user_name, "api_user_password": self.api_user_password}
    return self.request_post(self.api_login_url)
  
  def request_post(self, url: str):
    if not self.data:
      raise PasteBin_NoRequestData()
    r = requests.post(url=url, data=self.data)
    if "Bad API request" in r.text:
      raise PasteBin_BadAPIRequest(r.text)
    self.data = None
    return r.text
  
  def list_files(self, api_result_limit: str = 200):
    if not hasattr(self, "api_user_key") or not self.api_user_key:
      raise PasteBin_UserKeyRequired("list_files")

    self.data = {"api_dev_key": self.api_dev_key, "api_user_key": self.api_user_key, "api_option": "list", "api_result_limit": api_result_limit}
    file_list_str = self.request_post(self.api_post_url)

    files = dict()
    while "</paste>" in file_list_str:
      curr_paste = csf.in_bw(file_list_str, "<paste>", "</paste>")
      file_list_str = csf.after(file_list_str, "</paste>")
      files[csf.in_bw(curr_paste, "<paste_title>", "</paste_title>")] = csf.in_bw(curr_paste, "<paste_key>", "</paste_key>")
    return files

  def new_paste(self, api_paste_code: str, api_paste_name: str = "", api_paste_format: str = "", api_paste_private: str = "1", api_paste_expire_date: str = "N", api_folder_key: str = ""):
    if not hasattr(self, "api_user_key") or not self.api_user_key:
      self.data = {"api_dev_key": self.api_dev_key, "api_option": "paste", "api_paste_code": api_paste_code, "api_paste_name": api_paste_name, "api_paste_format": api_paste_format, "api_paste_private": api_paste_private, "api_paste_expire_date": api_paste_expire_date}
      return self.request_post(self.api_post_url)
    
    self.data = {"api_dev_key": self.api_dev_key, "api_user_key": self.api_user_key, "api_option": "paste", "api_paste_code": api_paste_code, "api_paste_name": api_paste_name, "api_paste_format": api_paste_format, "api_paste_private": api_paste_private, "api_paste_expire_date": api_paste_expire_date , "api_folder_key": api_folder_key}
    return self.request_post(self.api_post_url)

  def delete_paste(self, api_paste_key: str):
    if not hasattr(self, "api_user_key") or not self.api_user_key:
      raise PasteBin_UserKeyRequired("delete_paste")
    
    paste_data = self.get_paste(api_paste_key)
    self.data = {"api_dev_key": self.api_dev_key, "api_user_key": self.api_user_key, "api_option": "delete", "api_paste_key": api_paste_key}
    self.request_post(self.api_post_url)
    return paste_data
  
  def get_paste(self, api_paste_key: str):
    if not hasattr(self, "api_user_key") or not self.api_user_key:
      self.data = {"api_dev_key": self.api_dev_key, "api_option": "show_paste", "api_paste_key": api_paste_key}
      return self.request_post(self.api_raw_url)
      
    self.data = {"api_dev_key": self.api_dev_key, "api_user_key": self.api_user_key, "api_option": "show_paste", "api_paste_key": api_paste_key}
    return self.request_post(self.api_raw_url)

class PasteBin_main:
  def __init__(self, api_dev_key_main: str = None, api_user_name_main: str = None, api_user_password_main: str = None):
    if (api_dev_key_main == None):
      api_dev_key_main = os.environ["PASTEBIN_API_DEV_KEY_MAIN"]
    if (api_user_name_main == None):
      api_user_name_main = os.environ["PASTEBIN_API_USER_NAME_MAIN"]
    if (api_user_password_main == None):
      api_user_password_main  = os.environ["PASTEBIN_API_USER_PASSWORD_MAIN"]

    if not api_dev_key_main or not api_user_name_main or not api_user_password_main:
      raise PasteBin_NoDevKey()
    
    self.api_dev_key_main = api_dev_key_main
    self.api_user_name_main = api_user_name_main
    self.api_user_password_main = api_user_password_main

    self.pb = PasteBin(self, api_dev_key_main, api_user_name_main, api_user_password_main)
    self.api_user_key_main = self.pb.get_user_key()

    file_list = self.pb.list_files()
    self.main_key = file_list["main"]
    self.main_file_data = self.pb.get_paste(self.main_key)
  
  def scan_main_file(self):
    self.main = dict()
    self.main["bot"] = csf.in_bw(self.main_file_data, "<bot>", "</bot>")
    dq_str = csf.in_bw(self.main_file_data, "<dq>", "</dq>")
    self.main["dq"] = dict()
    self.main["dq"]["settings"] = csf.in_bw(dq_str, "<dq_settings>", "</dq_settings>")
    self.main["dq"]["ques_dump"] = csf.in_bw(dq_str, "<dq_ques_dump>", "</dq_ques_dump>")
    self.main["dq"]["ques_posted"] = csf.in_bw(dq_str, "<dq_ques_posted>", "</dq_ques_dump>")
    self.main["dq"]["days"] = dict()
    while "</dq_d>" in dq_str:
      curr_day = csf.in_bw(dq_str, "<dq_d>", "</dq_d>")
      dq_str = csf.after(dq_str, "</dq_d>")
      self.main["dq"]["days"][csf.in_bw(curr_day, "<n>", "</n>")] = csf.in_bw(curr_day, "<k>", "</k>")
  
  def write(self):
    old_main = self.pb.delete_paste(self.main)
    self.main_key = self.pb.new_paste(self.to_str, "main", "HTML", "2")
    return old_main

  def to_str(self):
    string = ""
    string += f"<bot>{self.main['bot']}</bot>\n"
    string += "<dq>\n"
    string += f"<dq_settings>{self.main['dq']['settings']}</dq_settings>\n"
    string += f"<dq_ques_dump>{self.main['dq']['ques_dump']}</dq_ques_dump>\n"
    string += f"<dq_ques_posted>{self.main['dq']['ques_posted']}</dq_ques_posted>\n"
    for k, v in self.main["dq"]["days"]:
      string += f"<dq_d><n>{k}</n><k>{v}</k></dq_d>\n"
    string += "</dq>"
  
  def get_file(self, api_paste_key: str):
    pb = PasteBin()
    return pb.get_paste(api_paste_key)
  
  def get_bot_config(self):
    pb = PasteBin()
    return pb.get_paste(self.main["bot"])

  def edit_dq_file(self, file_name: str, file_data: str):
    pb = PasteBin()
    old_paste = pb.delete_paste(self.main["dq"][file_name])
    self.main["dq"][file_name] = pb.new_paste(file_data, file_name + ".data", "HTML", "2", "N", os.environ["PASTEBIN_DQ_FOLDER_KEY"])
    self.write()
    return old_paste
  
  def get_day_list(self):
    return self.main["dq"]["days"]
  
  def add_dq_day(self, file_name: str, file_data: str):
    if file_name in self.main["dq"]["days"]:
      raise PasteBin_main_DayAlreadyExists(file_name)
    
    pb = PasteBin()
    self.main["dq"]["days"][file_name] = pb.new_paste(file_data, file_name + ".data", "HTML", "2", "N", os.environ["PASTEBIN_DQ_FOLDER_KEY"])
    self.write()
  
  def remove_dq_day(self, file_name: str):
    if file_name not in self.main["dq"]["days"]:
      raise PasteBin_main_DayNotFound(file_name)
    
    pb = PasteBin()
    old_paste = pb.delete_paste(self.main["dq"]["days"][file_name])
    self.write()
    return old_paste
  
  def get_dq_day(self, file_name: str):
    if file_name not in self.main["dq"]["days"]:
      raise PasteBin_main_DayNotFound(file_name)
    
    pb = PasteBin()
    return pb.get_paste(self.main["dq"]["days"][file_name])