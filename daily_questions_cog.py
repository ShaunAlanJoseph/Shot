from discord.ext import commands, tasks
import custom_string_functions as csf
import custom_random_functions as crf
import custom_discord_functions as cdf
import daily_questions as DQ
from datetime import datetime, timedelta
from Data import emojis
import traceback

dq_admin_users = None
dq_admin_roles = None


def is_dq_admin():
    async def predicate(ctx):
        if cdf.check_has_role(ctx.author, dq_admin_roles) or cdf.check_user_in_list(ctx.author, dq_admin_users):
            return True
        await ctx.reply(f"Imagine not having the perms to run that command. {emojis.sneezing_face}")
        return False

    return commands.check(predicate)


class DailyQuestions_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dq = DQ.DailyQuestions()
        dq_settings = self.dq.get_settings()
        global dq_admin_users, dq_admin_roles
        dq_admin_users = {x for x in dq_settings.admin_users}
        dq_admin_roles = {x for x in dq_settings.admin_roles}
        self.dq_time = dq_settings.time
        self.dq_ques_chnl = dq_settings.ques_chnl
        self.dq_soln_chnl = dq_settings.soln_chnl
        self.dq_announcement_chnl = dq_settings.announcement_chnl
        self.dq_admin_chnl = dq_settings.admin_chnl
        self.check_dq_time.start()

    async def cog_command_error(self, ctx, error):
        traceback.print_exc()
        await ctx.reply(f"Error: {error}.")

    @commands.command(name="dq.ping", description="Pongs you...duh!")
    @is_dq_admin()
    async def dq_ping(self, ctx):
        await ctx.send(f"{ctx.author.mention} pong!!")

    @commands.command(name="dq.add")
    @is_dq_admin()
    async def dq_add_day(self, ctx):
        new_day = csf.in_bw(ctx.message.content, "```", "```")
        new_day = self.dq.add_day(new_day)
        await ctx.reply(f"Questions for {new_day.nth}) -> {new_day.date.strftime('%Y-%m-%d')} ({new_day.durn}) have been added.", mention_author=False)

    @commands.command(name="dq.remove")
    @is_dq_admin()
    async def dq_remove_day(self, ctx, old_day):
        old_day = get_nth_or_date(old_day)
        old_day = self.dq.remove_day(old_day)
        await ctx.reply(f"Removed day: {old_day.nth}) -> {old_day.date.strftime('%Y-%m-%d')} ({old_day.durn}).\n**Raw:**\n```\n{old_day.to_str()}\n```", mention_author=False)

    @commands.command(name="dq.replace")
    @is_dq_admin()
    async def dq_update_day(self, ctx, old_day):
        old_day = get_nth_or_date(old_day)
        new_day = csf.in_bw(ctx.message.content, "```", "```")
        old_day = self.dq.update_day(old_day, new_day)
        await ctx.reply(f"Old day: {old_day.nth}) -> {old_day.date.strftime('%Y-%m-%d')} ({old_day.durn}).\n**Raw:**\n```\n{old_day.to_str()}\n```", mention_author=False)

    @commands.command(name="dq.list_days")
    @is_dq_admin()
    async def dq_list_days(self, ctx):
        day_list = self.dq.get_day_list()
        msg = ""
        for x in day_list:
            msg += f"{x['nth']}) -> {x['date'].strftime('%Y-%m-%d')} ({x['durn']})\n"
        await ctx.reply(f"Here is a list of days:\n{msg}", mention_author=False)

    @commands.command(name="dq.get_day_raw")
    @is_dq_admin()
    async def dq_get_day_raw(self, ctx, day):
        day = get_nth_or_date(day)
        day = self.dq.get_day(day)
        await ctx.reply(f"```\n{day.to_str()}\n```", mention_author=False)

    @commands.command(name="dq.announce_ques")
    @is_dq_admin()
    async def dq_announce_ques(self, ctx, date):
        day = get_nth_or_date(date)
        await self.announce_ques(self.dq.get_day(day))

    @commands.command(name="dq.announce_soln")
    @is_dq_admin()
    async def dq_announce_soln(self, ctx, date):
        day = get_nth_or_date(date)
        await self.announce_soln(self.dq.get_day(day))

    @commands.command(name="dq.announce")
    @is_dq_admin()
    async def dq_announce_ques_and_soln(self, ctx):
        await self.announce_questions_and_soln()

    @commands.command(name="dq.get_day_format")
    @is_dq_admin()
    async def dq_get_day_format(self, ctx):
        day_format = """```
<d_nth></d_nth>
<d_date></d_date>
<d_duration>1</d_duration>
<d_note></d_note>
<q>
<q_n>1</q_n>
<q_lvl></q_lvl>
<q_pts></q_pts>
<q_link></q_link>
<q_note></q_note>
<q_soln></q_soln>
</q>
<q>
<q_n>2</q_n>
<q_lvl></q_lvl>
<q_pts></q_pts>
<q_link></q_link>
<q_note></q_note>
<q_soln></q_soln>
</q>
```"""
        await ctx.reply(f"{day_format}", mention_author=False)

    @commands.command(name="dq.set_settings")
    @is_dq_admin()
    async def dq_set_details(self, ctx):
        dq_settings = csf.in_bw(ctx.message.content, "```", "```")
        dq_settings = self.dq.set_settings(dq_settings)
        global dq_admin_users, dq_admin_roles
        dq_admin_users = {x for x in dq_settings.admin_users}
        dq_admin_roles = {x for x in dq_settings.admin_roles}
        self.dq_time = dq_settings.time
        self.dq_ques_chnl = dq_settings.ques_chnl
        self.dq_soln_chnl = dq_settings.soln_chnl
        self.dq_announcement_chnl = dq_settings.announcement_chnl
        self.dq_admin_chnl = dq_settings.admin_chnl
        await ctx.reply(f"Daily Questions settings have been set.\n{dq_settings.to_str()}", mention_author=False)

    @commands.command(name="dq.get_settings")
    @is_dq_admin()
    async def dq_get_settings(self, ctx):
        dq_settings = self.dq.get_settings()
        await ctx.reply(f"Current settings for Daily Questions:\n```{dq_settings.to_str()}\n```", mention_author=False)

    @commands.command(name="dq.reset_posted")
    @is_dq_admin()
    async def dq_reset_posted(self, ctx, date):
        pass

    @tasks.loop(seconds=45)
    async def check_dq_time(self):
        curr_time = datetime.now() + timedelta(hours=5, minutes=30)  # converting utc to ist
        if self.dq_time.strftime('%H:%M') == curr_time.strftime('%H:%M'):
            print(f"dq: {self.dq_time.strftime('%H:%M')} now: {curr_time.strftime('%H:%M')} Now is the time!")
            await self.announce_questions_and_soln()
        else:
            print(f"dq: {self.dq_time.strftime('%H:%M')} now: {curr_time.strftime('%H:%M')}")

    @check_dq_time.before_loop
    async def before_check_dq_time(self):
        await self.bot.wait_until_ready()

    async def announce_questions_and_soln(self):
        pass

    async def announce_ques(self, day: DQ.DailyQuestions_Day):
        try:
            ques_msg = day.to_announce_ques()
            ques_chnl = await cdf.check_valid_channel(self.bot, self.dq_ques_chnl)
            await ques_chnl.send(ques_msg["title"])
            for x in ques_msg["questions"]:
                msg = await ques_chnl.send(x)
                await msg.add_reaction(emojis.white_check_mark)
        except Exception as ex:
            traceback.print_exc()

    async def announce_soln(self, day: DQ.DailyQuestions_Day):
        try:
            soln_msg = day.to_announce_soln()
            soln_chnl = await cdf.check_valid_channel(self.bot, self.dq_soln_chnl)
            await soln_chnl.send(soln_msg["title"])
            for x in soln_msg["questions"]:
                msg = ""
                for y in x:
                    msg = await soln_chnl.send(y)
                await msg.add_reaction(emojis.sparkles)
        except Exception as ex:
            traceback.print_exc()


async def setup(bot):
    await bot.add_cog(DailyQuestions_Cog(bot))


def get_nth_or_date(date: str):
    if date.isdigit():
        date = crf.check_valid_date(date)
        return date
    else:
        return int(date)
