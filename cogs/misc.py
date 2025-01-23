import logging
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timezone
from utils.checks import is_owner


class Misc(commands.Cog):
    """Miscellaneous commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["v"])
    async def version(self, ctx):
        """Display Zur'ok's current version"""
        await ctx.send(self.bot.version)

    @commands.command()
    async def age(self, ctx: Context):
        """Displays Zur'ok's age"""
        _age = datetime.now(timezone.utc) - self.bot.user.created_at
        years = _age.days // 365
        days = _age.days % 365

        await ctx.send(f"{years} years & {days} days")

    @commands.command(aliases=["bday"])
    async def birthday(self, ctx: Context):
        """Displays Zur'ok's birthday"""
        # self.bot.user.created_at
        await ctx.send(self.bot.user.created_at.strftime("%d %B"))

    @commands.command(hidden=True)
    @commands.check(is_owner)
    async def react(self, ctx: Context, channel_id: int, msg_id: int, *emojis):
        """React to a message in a channel"""
        channel = await self.bot.fetch_channel(channel_id)
        message = await channel.fetch_message(msg_id)
        for emoji in emojis:
            await message.add_reaction(emoji)

    @commands.command(hidden=True)
    @commands.check(is_owner)
    async def relay(self, ctx: Context, channel_id: int, *msg):
        """Send a message to a channel"""
        channel = await self.bot.fetch_channel(channel_id)
        await channel.send(" ".join(msg))


async def setup(bot):
    await bot.add_cog(Misc(bot))
