from datetime import datetime
from typing import Union


class DailyQuestions_InvalidArgumentType(Exception):
    def __init__(self, argument):
        self.message = f"Invalid argument type passed: {type(argument)}."
        super().__init__(self.message)


class DailyQuestions_RequiredAttribute(Exception):
    def __init__(self, attribute: str):
        self.message = f"Required attribute: {attribute}"
        super().__init__(self.message)


class DailyQuestions_UnableToGetPaste(Exception):
    def __init__(self, paste_key: str):
        self.message = f"Unable to access paste: {paste_key}"
        super().__init__(self.message)


class DailyQuestions_DayNotFound(Exception):
    def __init__(self, curr_day: Union[int, datetime]):
        if isinstance(curr_day, int):
            self.message = f"Day not found: {curr_day}"
        elif isinstance(curr_day, datetime):
            self.message = f"Day not found: {curr_day.strftime('%d-%m-%Y')}"
        else:
            self.message = f"Day not found."
        super().__init__(self.message)


class DailyQuestions_NewDayClash(Exception):
    def __init__(self, clashing_days: set):
        self.message = f"Day being added clashes with: {clashing_days}"
        super().__init__(self.message)


class DailyQuestions_NewQuestionClash(Exception):
    def __init__(self):
        self.message = f"Question begin added clashes with existing question."
        super().__init__(self.message)


# class DailyQuestions_NeitherDatetimeNotNth(Exception):
#   def __init__(self, attribute: str):
#     self.message = f"Neither datetime nor nth: {attribute}"
#     super().__init__(self.message)
