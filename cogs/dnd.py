import logging
from discord.ext import commands
from discord.ext.commands import Context
import random


class DnD(commands.Cog):
    """D&D and other RPG related commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def dnd(self, ctx):
        """D&D related commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Try '{self.bot.cfg.prefix}help dnd' to see available sub-commands.")

    @dnd.command()
    async def stats(self, ctx: Context):
        """Roll 4d6 drop lowest for D&D PC stats"""
        rolls = sorted([sum(sorted([random.randint(1, 6) for x in range(4)])[1:]) for y in range(6)])
        await ctx.send(", ".join([str(i) for i in rolls]))


async def setup(bot):
    await bot.add_cog(DnD(bot))
