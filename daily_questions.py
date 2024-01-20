from mongodb_reader import get_mongo_client
import custom_string_functions as csf
import custom_random_functions as crf
from DailyQuestions import daily_question_errors as dqe
from datetime import datetime, timedelta
from typing import Union
from requests import get


class DailyQuestions_Question:
    def __init__(self, curr_ques: Union[str, dict]) -> None:
        self.nth = None
        self.lvl = None
        self.pts = None
        self.link = None
        self.link_dtls = None
        self.note = None
        self.soln = None
        self.solnby = None
        self.q_msg = None
        self.slvd = None
        if isinstance(curr_ques, str):
            self.load_from_str(curr_ques)
        elif isinstance(curr_ques, dict):
            self.load_from_dict(curr_ques)
        else:
            raise dqe.DailyQuestions_InvalidArgumentType(curr_ques)

    def load_from_str(self, curr_ques_str: str) -> None:
        self.nth = int(read_tag(curr_ques_str, "q_n"))
        self.lvl = get_level(read_tag(curr_ques_str, "q_lvl"))
        self.pts = read_tag(curr_ques_str, "q_pts")
        self.pts = int(self.pts) if self.pts else 0
        self.link = read_tag(curr_ques_str, "q_link")
        self.link_dtls = format_link(self.link)
        self.note = read_tag(curr_ques_str, "q_note")
        self.soln = read_tag(curr_ques_str, "q_soln")
        self.solnby = read_tag(curr_ques_str, "q_solnby")
        self.solnby = int(self.solnby) if self.solnby else 0
        self.q_msg = read_tag(curr_ques_str, "q_msg")
        self.q_msg = int(self.q_msg) if self.q_msg else 0
        self.slvd = read_tag(curr_ques_str, "slvd").split(";")
        self.slvd = [int(x) for x in self.slvd if x]
        self.validate()

    def load_from_dict(self, curr_ques: dict) -> None:
        self.nth = curr_ques["nth"]
        self.lvl = curr_ques["lvl"]
        self.pts = curr_ques["pts"]
        self.link = curr_ques["link"]
        self.link_dtls = curr_ques["link_dtls"]
        self.note = curr_ques["note"]
        self.soln = curr_ques["soln"]
        self.solnby = curr_ques["solnby"]
        self.q_msg = curr_ques["q_msg"]
        self.slvd = curr_ques["slvd"]
        self.validate()

    def validate(self) -> None:
        if not self.nth:
            raise dqe.DailyQuestions_RequiredAttribute("nth")
        if not self.link:
            raise dqe.DailyQuestions_RequiredAttribute("link")

    def to_str(self) -> str:
        curr_day_str = ""
        curr_day_str += add_tags(self.nth, "q_n") + "\n"
        curr_day_str += add_tags(self.lvl, "q_lvl") + "\n"
        curr_day_str += add_tags(self.pts, "q_pts") + "\n"
        curr_day_str += add_tags(self.link, "q_link") + "\n"
        curr_day_str += add_tags(self.note, "q_note") + "\n"
        curr_day_str += add_tags(self.soln, "q_soln") + "\n"
        curr_day_str += add_tags(self.solnby, "q_solnby") + "\n"
        curr_day_str += add_tags(self.q_msg, "q_msg") + "\n"
        curr_day_str += add_tags(";".join([str(x) for x in self.slvd]), "q_slvd")
        return curr_day_str

    def to_dict(self) -> dict:
        curr_day = dict()
        curr_day["type"] = "ques"
        curr_day["nth"] = self.nth
        curr_day["lvl"] = self.lvl
        curr_day["pts"] = self.pts
        curr_day["link"] = self.link
        curr_day["link_dtls"] = self.link_dtls
        curr_day["note"] = self.note
        curr_day["soln"] = self.soln
        curr_day["solnby"] = self.solnby
        curr_day["q_msg"] = self.q_msg
        curr_day["slvd"] = self.slvd
        return curr_day


class DailyQuestions_Day:
    def __init__(self, curr_day: Union[str, dict]) -> None:
        self.nth = None
        self.date = None
        self.durn = None
        self.note = None
        self.posted = None  # 0 -> not posted, 1 -> ques posted, 2 -> soln posted
        self.ques = list()
        if isinstance(curr_day, str):
            self.load_from_str(curr_day)
        elif isinstance(curr_day, dict):
            self.load_from_dict(curr_day)
        else:
            raise dqe.DailyQuestions_InvalidArgumentType(curr_day)

    def load_from_str(self, curr_day_str: str) -> None:
        self.nth = read_tag(curr_day_str, "d_nth")
        self.nth = int(self.nth) if self.nth else 0
        self.date = crf.check_valid_date(read_tag(curr_day_str, "d_date"))
        self.durn = read_tag(curr_day_str, "d_durn")
        self.durn = int(self.durn) if self.durn else 0
        self.note = read_tag(curr_day_str, "note")
        self.posted = read_tag(curr_day_str, "posted")
        self.posted = int(self.posted) if self.posted else 0
        while "</q>" in curr_day_str:
            curr_ques_str = read_tag(curr_day_str, "q")
            curr_day_str = csf.after(curr_day_str, "</q>")
            curr_ques = DailyQuestions_Question(curr_ques_str)
            self.ques.append(curr_ques)
        self.ques = sorted(self.ques, key=lambda obj: obj.nth)
        self.validate()

    def load_from_dict(self, curr_day: dict) -> None:
        self.nth = curr_day["nth"]
        self.date = curr_day["date"]
        self.durn = curr_day["durn"]
        self.note = curr_day["note"]
        self.posted = curr_day["posted"]
        for curr_ques in curr_day["ques"]:
            curr_ques = DailyQuestions_Question(curr_ques)
            self.ques.append(curr_ques)
        self.ques = sorted(self.ques, key=lambda obj: obj.nth)
        self.validate()

    def validate(self) -> None:
        if not self.nth:
            raise dqe.DailyQuestions_RequiredAttribute("nth")
        if not self.date:
            raise dqe.DailyQuestions_RequiredAttribute("date")
        if not self.durn:
            raise dqe.DailyQuestions_RequiredAttribute("durn")
        if not self.ques:
            raise dqe.DailyQuestions_RequiredAttribute("ques")

    def to_str(self) -> str:
        curr_day_str = ""
        curr_day_str += add_tags(self.nth, "d_nth") + "\n"
        curr_day_str += add_tags(self.date.strftime("%d-%m-%Y"), "d_date") + "\n"
        curr_day_str += add_tags(self.durn, "d_durn") + "\n"
        curr_day_str += add_tags(self.note, "d_note") + "\n"
        curr_day_str += add_tags(self.posted, "d_posted") + "\n"
        for x in self.ques:
            curr_day_str += "<q>\n"
            curr_day_str += x.to_str()
            curr_day_str += "\n</q>\n"
        curr_day_str.rstrip("\n")
        return curr_day_str

    def to_dict(self) -> dict:
        curr_day = dict()
        curr_day["type"] = "day"
        curr_day["nth"] = self.nth
        curr_day["date"] = self.date
        curr_day["durn"] = self.durn
        curr_day["note"] = self.note
        curr_day["posted"] = self.posted
        ques_list = list()
        for x in self.ques:
            ques_list.append(x.to_dict())
        curr_day["ques"] = sorted(ques_list, key=lambda ele: ele["nth"])
        return curr_day

    def to_mini_dict(self) -> dict:
        curr_day = dict()
        curr_day["nth"] = self.nth
        curr_day["date"] = self.date
        curr_day["durn"] = self.durn
        return curr_day

    def to_announce_ques(self) -> dict:
        ques_msg = dict()
        ques_msg["title"] = f"**DAILY PROBLEMS (DAY{self.nth}{'' if (self.durn == 1) else f' - {self.nth + self.durn - 1}'}) - {self.date.strftime('%d-%m-%Y')}**"
        ques_msg["ques"] = list()
        if self.note:
            ques_msg["note"] = f"**Note:** {self.note}"
        for x in self.ques:
            curr_ques = f"**Question {x.nth}:**"
            if x.lvl:
                curr_ques += f"\n**Level:** {x.lvl}"
            if x.pts:
                curr_ques += f"\n**Points:** {x.pts}"
            curr_ques += f"\n**Link:** <{x.link}>"
            if x.note:
                curr_ques += f"\n**Note:** {x.note}"
            ques_msg["ques"].append(curr_ques)
        return ques_msg

    def to_announce_soln(self) -> dict:
        soln_msg = dict()
        soln_msg["title"] = f"**DAY{self.nth}{'' if (self.durn == 1) else f' - {self.nth + self.durn - 1}'} - {self.date.strftime('%d-%m-%Y')} - SOLUTIONS**"
        soln_msg["ques"] = list()
        for x in self.ques:
            curr_str = f"**Question {x.nth}:**"
            if x.lvl:
                curr_str += f"\n**Level:** {x.lvl}"
            curr_str += f"\n**Link:** <{x.link}>"
            curr_str += f"\n**Soln{f' (by <u>{x.solnby}</u>)' if x.solnby else ''}:**"
            if not x.soln:
                curr_str += f" SOLN NOT WRITTEN!!"
                soln_msg["ques"].append([curr_str])
                continue
            soln_list = soln_splitter(x.soln)
            soln_list[0] = f"{curr_str}\n{soln_list[0]}"
            soln_msg["ques"].append(soln_list)
        return soln_msg


class DailyQuestions_Settings:
    def __init__(self, curr_set: Union[str, dict]) -> None:
        self.time = None
        self.ques_chnl = None
        self.soln_chnl = None
        self.announcement_chnl = None
        self.admin_chnl = None
        self.admin_roles = None
        self.admin_users = None
        if isinstance(curr_set, str):
            self.load_from_str(curr_set)
        elif isinstance(curr_set, dict):
            self.load_from_dict(curr_set)
        else:
            raise dqe.DailyQuestions_InvalidArgumentType(curr_set)

    def load_from_str(self, curr_set_str: str) -> None:
        self.time = crf.check_valid_time(read_tag(curr_set_str, "time"))
        self.ques_chnl = int(read_tag(curr_set_str, "ques_chnl"))
        self.soln_chnl = int(read_tag(curr_set_str, "soln_chnl"))
        self.announcement_chnl = int(read_tag(curr_set_str, "announcement_chnl"))
        self.admin_chnl = int(read_tag(curr_set_str, "admin_chnl"))
        self.admin_roles = read_tag(curr_set_str, "admin_roles").split(";")
        self.admin_roles = [int(x) for x in self.admin_roles if x]
        self.admin_users = read_tag(curr_set_str, "admin_users").split(";")
        self.admin_users = [int(x) for x in self.admin_users if x]
        self.validate()

    def load_from_dict(self, curr_set: dict) -> None:
        self.time = curr_set["time"]
        self.ques_chnl = curr_set["ques_chnl"]
        self.soln_chnl = curr_set["soln_chnl"]
        self.announcement_chnl = curr_set["announcement_chnl"]
        self.admin_chnl = curr_set["admin_chnl"]
        self.admin_roles = curr_set["admin_roles"]
        self.admin_users = curr_set["admin_users"]
        self.validate()

    def validate(self) -> None:
        if not self.time:
            raise dqe.DailyQuestions_RequiredAttribute("time")
        if not self.ques_chnl:
            raise dqe.DailyQuestions_RequiredAttribute("ques_chnl")
        if not self.soln_chnl:
            raise dqe.DailyQuestions_RequiredAttribute("soln_chnl")
        if not self.announcement_chnl:
            raise dqe.DailyQuestions_RequiredAttribute("announcement_chnl")
        if not self.admin_chnl:
            raise dqe.DailyQuestions_RequiredAttribute("admin_chnl")
        if not self.admin_roles and not self.admin_users:
            raise dqe.DailyQuestions_RequiredAttribute("admin_roles or admin_users")

    def to_str(self) -> str:
        curr_set_str = ""
        curr_set_str += add_tags(self.time.strftime('%H:%M'), "time") + "\n"
        curr_set_str += add_tags(self.ques_chnl, "ques_chnl") + "\n"
        curr_set_str += add_tags(self.soln_chnl, "soln_chnl") + "\n"
        curr_set_str += add_tags(self.announcement_chnl, "announcement_chnl") + "\n"
        curr_set_str += add_tags(self.admin_chnl, "admin_chnl") + "\n"
        curr_set_str += add_tags(";".join([str(x) for x in self.admin_roles]), "admin_roles") + "\n"
        curr_set_str += add_tags(";".join([str(x) for x in self.admin_users]), "admin_users")
        return curr_set_str

    def to_dict(self) -> dict:
        curr_set = dict()
        curr_set["type"] = "settings"
        curr_set["time"] = self.time
        curr_set["ques_chnl"] = self.ques_chnl
        curr_set["soln_chnl"] = self.soln_chnl
        curr_set["announcement_chnl"] = self.announcement_chnl
        curr_set["admin_chnl"] = self.admin_chnl
        curr_set["admin_roles"] = self.admin_roles
        curr_set["admin_users"] = self.admin_users
        return curr_set


class DailyQuestions:
    def __init__(self) -> None:
        self.client = get_mongo_client()
        self.Days = self.client.DailyQuestions.Days
        self.Additional = self.client.DailyQuestions.Additional

    def add_day(self, new_day_str: str) -> DailyQuestions_Day:
        new_day = DailyQuestions_Day(new_day_str)
        clashing_days = self.get_clashing_days(new_day)
        if clashing_days:
            raise dqe.DailyQuestions_NewDayClash(clashing_days)
        for x in new_day.ques:
            if self.Days.count_documents({"type": "day", "ques": {"link_dtls": x.link_dtls}}):
                raise dqe.DailyQuestions_NewQuestionClash()
        self.Days.insert_one(new_day.to_dict())
        return new_day

    def remove_day(self, old_day: Union[int, datetime]) -> DailyQuestions_Day:
        old_day_obj = self.get_day(old_day)
        if isinstance(old_day, int):
            self.Days.delete_one({"type": "day", "nth": old_day})
        elif isinstance(old_day, datetime):
            self.Days.delete_one({"type": "day", "date": old_day})
        else:
            raise dqe.DailyQuestions_InvalidArgumentType(old_day)
        return old_day_obj

    def update_day(self, old_day: Union[int, datetime], new_day_str: str) -> DailyQuestions_Day:
        old_day_obj = self.get_day(old_day)
        new_day = DailyQuestions_Day(new_day_str)
        clashing_days_set = self.get_clashing_days(new_day)
        clashing_day = dict(clashing_days_set.pop())
        if clashing_days_set or old_day_obj.to_mini_dict() != clashing_day:
            raise dqe.DailyQuestions_NewDayClash(clashing_days_set)
        for x in new_day.ques:
            ques_clash = self.Days.find_one({"type": "day", "ques": {"link_dtls": x.link_dtls}},
                                            {"nth": 1, "date": 1, "durn": 1})
            if not ques_clash:
                continue

            if ques_clash.pop("_id") != clashing_day:
                raise dqe.DailyQuestions_NewQuestionClash()
        self.Days.update_one({"type": "day", "nth": old_day_obj.nth}, {"$set": new_day.to_dict()})
        return old_day_obj

    def get_day(self, curr_day: Union[int, datetime]) -> DailyQuestions_Day:
        if isinstance(curr_day, int):
            result = self.Days.find_one({"type": "day", "nth": curr_day})
        elif isinstance(curr_day, datetime):
            result = self.Days.find_one({"type": "day", "date": curr_day})
        else:
            raise dqe.DailyQuestions_InvalidArgumentType(curr_day)
        if not result:
            raise dqe.DailyQuestions_DayNotFound(curr_day)
        return DailyQuestions_Day(result)

    def get_clashing_days(self, curr_day: DailyQuestions_Day) -> set:
        clashing_days = set()
        day_list = self.get_day_list()
        for x in day_list:
            if x["nth"] == curr_day.nth:
                clashing_days.add(frozenset(x.items()))
            if x["date"] <= curr_day.date < x["date"] + timedelta(days=x["durn"]):
                clashing_days.add(frozenset(x.items()))
        return clashing_days

    def get_day_list(self) -> list:
        result = self.Days.find({"type": "day"}, {"nth": 1, "date": 1, "durn": 1}).sort("nth")
        result = list(result)
        for i in range(0, len(result)):
            result[i].pop("_id")
        return result

    def get_settings(self) -> DailyQuestions_Settings:
        result = self.Additional.find_one({"type": "settings"})
        return DailyQuestions_Settings(result)

    def set_settings(self, new_settings_str: str) -> DailyQuestions_Settings:
        new_settings = DailyQuestions_Settings(new_settings_str)
        old_settings = self.get_settings()
        self.Additional.update_one({"type": "settings"}, {"$set": new_settings.to_dict()})
        return old_settings


def format_link(link) -> dict:
    link.rstrip("/")
    link_dtls = dict()
    if "codeforces.com" in link:
        link_dtls["pf"] = "CF"
        ques_letter = link[csf.last_occurance(link, "/") + 1:]
        link_dtls["ques"] = "-" + ques_letter
        ques_link = link
        while "/" in ques_link:
            contest_num = csf.before(ques_link, "/")
            if contest_num.isdigit():
                link_dtls["ques"] = contest_num + link_dtls["ques"]
                break
            ques_link = csf.after(ques_link, "/")

    elif "codechef.com" in link:
        link_dtls["pf"] = "CC"
        link_dtls["ques"] = link[csf.last_occurance(link, "/") + 1:]

    elif "cses.fi" in link:
        link_dtls["pf"] = "CS"
        link_dtls["ques"] = link[csf.last_occurance(link, "/") + 1:]

    else:
        link_dtls["pf"] = "OT"
        link_dtls["ques"] = link

    return link_dtls


def read_tag(haystack: str, tag: str) -> str:
    return csf.in_bw(haystack, f"<{tag}>", f"</{tag}>")


def add_tags(haystack: str, tag: str) -> str:
    return f"<{tag}>{haystack}</{tag}>"


def soln_splitter(soln_str: str) -> list:
    while "</pb>" in soln_str:
        paste_key = read_tag(soln_str, "pb")
        paste_data = get_from_pastebin(paste_key)
        soln_str = csf.replace(soln_str, add_tags(paste_key, "pb"), paste_data, 1)
    soln_str = csf.replace(soln_str, "<img>", "<br>")
    soln_str = csf.replace(soln_str, "</img>", "<br>")
    soln_list = soln_str.split("<br>")
    soln_list = [x for x in soln_list if x.strip()]
    return soln_list


def get_from_pastebin(paste_key: str) -> str:
    r = get(f"https://pastebin.com/raw/{paste_key}")
    if r.reason != "OK":
        raise dqe.DailyQuestions_UnableToGetPaste(paste_key)
    return r.text


def get_level(level) -> str:
    if level in ["Cakewalk", "Easy", "Medium", "Hard", "Giveup", "Cakewalk-Easy", "Easy-Medium", "Medium-Hard",
                 "Hard-Giveup"]:
        return level
    elif level == 'C':
        return "Cakewalk"
    elif level == 'E':
        return "Easy"
    elif level == 'M':
        return "Medium"
    elif level == 'H':
        return "Hard"
    elif level == 'G':
        return "Giveup"
    elif level == "CE":
        return "Cakewalk-Easy"
    elif level == "EM":
        return "Easy-Medium"
    elif level == "MH":
        return "Medium-Hard"
    elif level == "HG":
        return "Hard-Giveup"
    else:
        return "Not Defined"
