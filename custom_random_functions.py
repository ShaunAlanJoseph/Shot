from datetime import datetime
from typing import Union
import custom_string_functions as csf


class InvalidTimeStr(Exception):
    """Raised if the time string passed to check_valid_time() is invalid."""

    def __init__(self, time):
        self.message = f"Invalid time: {time}."
        super().__init__(self.message)


def check_valid_time(time: Union[str, datetime]):
    if isinstance(time, datetime):
        return check_valid_time(time.strftime('%H:%M:%S:%f'))
    separator = ""
    if " " in time:
        separator = " "
    elif "-" in time:
        separator = "-"
    elif "." in time:
        separator = "."
    else:
        separator = ":"
    try:
        hours = 0
        mins = 0
        secs = 0
        mus = 0
        if separator in time:
            hours = int(csf.before(time, separator))
            temp_str = csf.after(time, separator)
            if separator in temp_str:
                mins = int(csf.before(temp_str, separator))
                temp_str = csf.after(time, separator)
                if separator in temp_str:
                    secs = int(csf.before(temp_str, separator))
                    mus = int(csf.after(time, separator))
                else:
                    secs = int(temp_str)
            else:
                mins = int(temp_str)
        else:
            hours = int(time)
        return datetime(1, 1, 1, hours, mins, secs, mus)
    except:
        raise InvalidTimeStr(time)


class InvalidDateStr(Exception):
    """Raised when the date string passed to check_valid_date() is invalid."""

    def __init__(self, date):
        self.message = f"Invalid date: {date}."
        super().__init__(self.message)


def check_valid_date(date: Union[str, datetime], year_first: bool = False):
    if isinstance(date, datetime):
        return check_valid_date(date.strftime('%d-%m-%Y'))
    separator = ""
    if "/" in date:
        separator = "/"
    elif "|" in date:
        separator = "|"
    elif "." in date:
        separator = "."
    elif " " in date:
        separator = " "
    elif ":" in date:
        separator = ":"
    else:
        separator = "-"
    try:
        if year_first:
            year = csf.before(date, separator)
            if len(year) == 2:
                year = "20" + year
            year = int(year)
            temp_str = csf.after(date, separator)
            month = int(csf.before(temp_str, separator))
            day = int(csf.after(temp_str, separator))
        else:
            day = int(csf.before(date, separator))
            temp_str = csf.after(date, separator)
            month = int(csf.before(temp_str, separator))
            year = csf.after(temp_str, separator)
            if len(year) == 2:
                year = "20" + year
            year = int(year)
        return datetime(year, month, day)
    except:
        raise InvalidDateStr(date)


class InvalidDateTimeStr(Exception):
    """Raised when the date string passed to check_valid_date() is invalid."""

    def __init__(self, dt):
        self.message = f"Invalid datetime: {dt}."
        super().__init__(self.message)


def check_valid_datetime(dt: Union[str, datetime]):
    if isinstance(dt, datetime):
        return check_valid_datetime(dt.strftime('%d-%m-%Y %H:%M'))
    try:
        dt_str = dt
        day = int(csf.before(dt_str, "-"))
        dt_str = csf.after(dt_str, "-")
        month = int(csf.before(dt_str, "-"))
        dt_str = csf.after(dt_str, "-")
        year = int(csf.before(dt_str, " "))
        dt_str = csf.after(dt_str, " ")
        hour = int(csf.before(dt_str, ":"))
        dt_str = csf.after(dt_str, ":")
        mins = int(dt_str)
        return datetime(year, month, day, hour, mins)
    except:
        raise InvalidDateTimeStr(dt)


def add_time_to_date(date: datetime, time: datetime):
    return datetime(date.year, date.month, date.day, time.hour, time.minute, time.second, time.microsecond)
