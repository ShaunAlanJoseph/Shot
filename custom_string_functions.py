def in_bw(haystack: str, before: str, after: str, include=0) -> str:
    if not after or not before:
        return ""

    pos1 = haystack.find(before)
    if (pos1 == -1):
        return ""

    haystack = haystack[pos1 + len(before):]
    pos2 = haystack.find(after)
    if pos2 == -1:
        return ""

    if include:
        return before + haystack[0: pos2] + after

    return haystack[0: pos2]


def after(haystack: str, before: str, include=0) -> str:
    if not before:
        return ""

    pos = haystack.find(before)

    if pos == -1:
        return ""

    if include:
        return haystack[pos:]

    return haystack[pos + len(before):]


def before(haystack: str, after: str, include=0) -> str:
    if not after:
        return ""

    pos = haystack.find(after)

    if pos == -1:
        return ""

    if include:
        return haystack[0: pos + len(after)]

    return haystack[0: pos]


def replace(haystack: str, needle: str, replace_with: str = "", count=-1) -> str:
    if not needle or not count:
        return haystack

    pos = haystack.find(needle)

    if pos == -1:
        return haystack

    return haystack[0: pos] + replace_with + replace(haystack[pos + len(needle):], needle, replace_with, count - 1)


def last_occurance(haystack: str, needle: str) -> int:
    pos = -1

    while True:
        temp_pos = haystack.find(needle)
        haystack = haystack[temp_pos + 1:]
        if temp_pos == -1:
            break
        pos += temp_pos + 1

    return pos


def replace_last_occurance(haystack: str, needle: str, replace_with="") -> str:
    if not needle:
        return haystack

    pos = last_occurance(haystack, needle)
    if pos == -1:
        return haystack

    if len(haystack) == len(needle) + pos:
        return haystack[0: pos] + replace_with
    return haystack[0: pos] + replace_with + haystack[pos + len(needle)]


"""
def angle_around_link(haystack): # not ready
  if "https://" not in haystack:
    return haystack
  
  b4 = before(haystack, "https://")
  haystack = after(haystack, "https://")
  link = before(haystack)
  return b4 + "<" + link + ">" + angle_around_link(haystack)
"""
