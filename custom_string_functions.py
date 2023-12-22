def str_in_bw(haystack, before, after, include = 0):
    
  if (not after or not before):
    return ""
  
  pos1 = haystack.find(before)
  if (pos1 == -1):
    return ""
  
  haystack = haystack[pos1 + len(before) :]
  pos2 = haystack.find(after)
  if (pos2 == -1):
    return ""
  
  if (include):
    return before + haystack[0: pos2] + after
  
  return haystack[0: pos2]

def str_after(haystack, before, include = 0):
  if not before:
    return haystack
  
  pos = haystack.find(before)
  
  if (pos == -1):
    return ""
  
  if (include):
    return haystack[pos :]
  
  return haystack[pos + len(before) :]

def str_before(haystack, after, include = 0):
  if not after:
    return haystack
  
  pos = haystack.find(after)

  if (pos == -1):
    return ""

  if (include):
    return haystack[0 : pos + len(after)]

  return haystack[0 : pos]

def str_replace(haystack, needle, str = ""):
  if not needle:
    return haystack
  
  pos = haystack.find(needle)
  
  if (pos == -1):
    return haystack
  
  return haystack[0 : pos] + str + str_replace(haystack[pos + len(needle) :], needle, str)