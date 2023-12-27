import discord
from discord.ext import commands, tasks

async def check_valid_user(bot, user_id):
  if isinstance(user_id, str) and user_id.isdigit():
    user_id = int(user_id)
  if not isinstance(user_id, int):
    print(f"Invalid user_id: {user_id}.")
    return None
  try:
    user_api = await bot.fetch_user(user_id)
    return user_api
  except discord.NotFound:
    print(f"Invalid user_id: {user_id}.")
    return None

async def check_valid_role(bot, guild_id, role_id):
  if isinstance(role_id, str) and role_id.isdigit():
    role_id = int(role_id)
  if not isinstance(role_id, int):
    print(f"Invalid role_id: {role_id}.")
    return None
  
  if isinstance(guild_id, str) and guild_id.isdigit():
    guild_id = int(guild_id)
  if not isinstance(guild_id, int):
    print(f"Invalid guild_id: {guild_id}.")
    return None
  
  guild = bot.get_guild(guild_id)
  if not guild:
    print(f"Invalid guild_id: {guild_id}.")
    return None
  
  try:
    role_api = await guild.fetch_role(role_id)
    return role_api
  except discord.NotFound:
    print(f"Invalid role_id: {role_id}.")
    return None

async def check_valid_channel(bot, channel_id):
  if isinstance(channel_id, str) and channel_id.isdigit():
    channel_id = int(channel_id)
  if not isinstance(channel_id, int):
    print(f"Invalid channel_id: {channel_id}.")
    return None

  try:
    channel_api = await bot.fetch_channel(channel_id)
    return channel_api
  except discord.NotFound:
    print(f"Invalid channel_id: {channel_id}.")
    return None

def check_has_role(user: discord.Member, role_list: list):
  user_roles = [role.id for role in user.roles]
  user_roles.sort()
  role_list.sort()
  a = 0; b = 0
  while (a < len(user_roles) and b < len(role_list)):
    if (user_roles[a] == role_list[b]):
      return True
    if (user_roles[a] < role_list[b]):
      a += 1
    else:
      b += 1
  return False

def check_user_in_list(user: discord.Member, user_id_list: list):
  if user.id in user_id_list:
    return True
  return False