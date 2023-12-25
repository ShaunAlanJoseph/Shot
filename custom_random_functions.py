from datetime import datetime
import custom_string_functions as csf

def check_valid_time(time_str: str):
  separator = ""
  if " " in time_str:
    separator = " "
  elif "-" in time_str:
    separator = "-"
  elif "." in time_str:
    separator = "."
  else:
    separator = ":"
  try:
    hours = 0; mins = 0; secs = 0; ms = 0
    if separator in time_str:
      hours = int(csf.str_before(time_str, separator))
      temp_str = csf.str_after(time_str, separator)
      if separator in temp_str:
        mins = int(csf.str_before(temp_str, separator))
        temp_str = csf.str_after(time_str, separator)
        if separator in temp_str:
          secs = int(csf.str_before(temp_str, separator))
          ms = int(csf.str_after(time_str, separator))
        else:
          secs = int(temp_str)
      else:
        mins = int(temp_str)
    else:
      hours = int(time_str)
    time = datetime(1, 1, 1, hours, mins, secs, ms)
    return time
  except:
    print(f"Invalid time_str: {time_str}.")
    return None

def check_valid_date(date_str: str):
  separator = ""
  if "/" in date_str:
    separator = "/"
  elif "|" in date_str:
    separator = "|"
  elif "." in date_str:
    separator = "."
  elif " " in date_str:
    separator = " "
  elif ":" in date_str:
    separator = ":"
  else:
    separator = "-"
  try:
    day = int(csf.str_before(date_str, separator))
    temp_str = csf.str_after(date_str, separator)
    month = int(csf.str_before(temp_str, separator))
    year = csf.str_after(temp_str, separator)
    if (len(year) == 2):
      year = "20" + year
    year = int(year)
    date = datetime(year, month, day)
    return date
  except:
    print(f"Invalid date_str: {date_str}.")
    return None