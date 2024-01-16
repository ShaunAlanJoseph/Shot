import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import custom_discord_functions as cdf
from Data import emojis
import asyncio
import traceback
import random
from mongodb_reader import get_mongo_client
from webserver import keep_alive


load_dotenv()
DISCORD_API_SECRET = os.environ['DISCORD_API_SECRET']
mongo_client = get_mongo_client()
bot_config = mongo_client.Shot.bot_config


def is_bot_admin():
    async def predicate(ctx):
        if cdf.check_has_role(ctx.author, bot_admin_roles) or cdf.check_user_in_list(ctx.author, bot_admin_users):
            return True
        await ctx.reply(f"What makes you think that you can run this command?? {emojis.sneezing_face}")
        return False

    return commands.check(predicate)


def config(key):
    result = bot_config.find_one({"name": key})
    return result["val"]


bot_admin_users = config("bot_admin_users")
bot_admin_roles = config("bot_admin_roles")


async def start():
    intents = discord.Intents.default()
    intents.message_content = True

    bot_msg_channel = ""

    bot = commands.Bot(command_prefix="!", intents=intents)

    await bot.load_extension("daily_questions_cog")

    @bot.event
    async def on_ready():
        print(f"Logged in as User: {bot.user} (ID: {bot.user.id})")
        print("------")
        await bot.tree.sync()
        nonlocal bot_msg_channel
        bot_msg_channel = bot.get_channel(config("bot_msg_chnl"))
        await bot_msg_channel.send(f"Hi, I've logged in as **User:** {bot.user} (**ID:** {bot.user.id})")
        update_presence.start()

    @bot.event
    async def on_command_error(ctx, error):
        traceback.print_exc()
        await ctx.reply(f"Error: {error}.", mention_author=False)

    @tasks.loop(seconds=30)
    async def update_presence():
        try:
            activity = ""
            bot_activity = random.randint(1, 5)
            if bot_activity == 1:
                member_count = 0
                for guild in bot.guilds:
                    if guild.member_count:
                        member_count += guild.member_count
                activity = discord.CustomActivity(f"{emojis.weary_face} Listening to {member_count} skill issues.")
            elif bot_activity == 2:
                activity = discord.CustomActivity(f"{emojis.lying_face} I'm a Grandmaster....fr fr")
            elif bot_activity == 3:
                activity = discord.CustomActivity(f"{emojis.blowing_kiss}")
            elif bot_activity == 4:
                activity = discord.CustomActivity(f"{emojis.nerd} Reading the CPH!! {emojis.paper}")
            elif bot_activity == 5:
                activity = discord.Activity(type=discord.ActivityType.listening, name=f"Test Drive {emojis.headphones}")
            else:
                activity = discord.CustomActivity(f"**Shaun's Bot!!**")
            await bot.change_presence(activity=activity)
        except Exception as ex:
            traceback.print_exc()

    @bot.event
    async def on_member_join(member: discord.Member):
        await update_presence()

    @bot.hybrid_command()
    @is_bot_admin()
    async def ping(ctx):
        await ctx.send(f"{ctx.author.mention} pong!")
        await ctx.author.send("I see that you ran a command.")

    @bot.command(name="dq.reload")
    @is_bot_admin()
    async def daily_question_reload(ctx):
        try:
            await bot.reload_extension("daily_questions_cog")
            await ctx.send(f"DailyQuestions_Cog has been reloaded successfully.")
            print(f"DailyQuestions_Cog reloaded successfully.")
        except:
            await ctx.send(f"Failed to reload DailyQuestions_Cog. Error: {Exception}")
            print(f"Failed to reload DailyQuestions_Cog. Error: {Exception}")

    await bot.start(DISCORD_API_SECRET)


if __name__ == "__main__":
    keep_alive()
    asyncio.run(start())
