import logging

import discord
from discord.ext import commands
from utils.checks import is_owner

from database.db import User, Guild


class Dev(commands.Cog):
    """Dev commands"""

    def __init__(self, bot):
        self.bot = bot

    def add_guild(self, guild: discord.Guild):
        if Guild.objects(guild_id=guild.id).count() == 0:
            Guild(guild_id=guild.id, name=guild.name).save()

    def add_user(self, member: discord.Member):
        if User.objects(discord=str(member.id)).count() == 0:
            user = User(member.name, str(member.id))
            user.display_name = member.global_name
            user.permissions = {"site": ["view"], "quotes": ["view", "hide"]}
            user.save()

        else:
            user = User.objects(discord=str(member.id)).first()

            if str(member.guild.id) not in user.tags:
                user.tags.append(str(member.guild.id))

            # user.permissions = {"site": ["view"], "quotes": ["view", "hide"]}
            user.save()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        logging.info("Member joined")
        self.add_user(member)

    @commands.group()
    @commands.check(is_owner)
    async def update(self, ctx):
        """Admin update commands"""
        if ctx.invoked_subcommand is None:
            pass

    @update.command(hidden=True)
    @commands.check(is_owner)
    async def guilds(self, ctx):
        for guild in self.bot.guilds:
            print(guild)
        await ctx.send("Done!")

    @update.command(hidden=True)
    @commands.check(is_owner)
    async def users(self, ctx):
        for guild in self.bot.guilds:
            print(guild)
            for member in guild.members:
                if member.bot:
                    continue
                print("    ", member)
                self.add_user(member)
        await ctx.send("Done!")

async def setup(bot):
    await bot.add_cog(Dev(bot))
