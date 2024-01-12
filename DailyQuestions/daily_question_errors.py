from datetime import datetime

class DailyQuestions_Question_InvalidQuestion(Exception):
  def __init__(self, file_path: str):
    self.file_path = file_path
    self.message = f"Invalid Question in file path: {self.file_path}."
    super().__init__(self.message)

class DailyQuestions_Day_FileNotFound(Exception):
  def __init__(self, file_path):
    if isinstance(file_path, datetime):
      self.file_path = file_path.strftime('%Y-%m-%d')
    else:
      self.file_path = file_path
    self.message = f"Invalid Daily Questions file path: {self.file_path}."
    super().__init__(self.message)

class DailyQuestions_Day_InvalidFileName(Exception):
  def __init__(self, file_path: str):
    self.file_path = file_path
    self.message = f"Invalid file name: {self.file_path}."
    super().__init__(self.message)

class DailyQuestions_Day_InvalidFileData(Exception):
  def __init__(self, file_path: str):
    self.file_path = file_path
    self.message = f"Invalid file data: {self.file_path}."
    super().__init__(self.message)

class DailyQuestions_Day_NoQuestions(Exception):
  def __init__(self, file_path: str):
    self.file_path = file_path
    self.message = f"No questions found in the file: {self.file_path}."
    super().__init__(self.message)

class DailyQuestions_Details_InvalidData(Exception):
  def __init__(self):
    self.message = f"Invalid change made to details."
    super().__init__(self.message)
    
class DailyQuestions_DayDetails_InvalidArguments(Exception):
  def __init__(self):
    self.message = f"Invalid set of arguments passed."
    super().__init__(self.message)

class DailyQuestions_AddDay_Clashing(Exception):
  def __init__(self):
    self.message = f"New day being added clashes with an existing day."
    super().__init__(self.message)