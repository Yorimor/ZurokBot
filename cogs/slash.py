import discord
from discord import app_commands
from discord.ext import commands
import random


class MyCog(commands.GroupCog, name="dnd"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()  # this is now required in this context.

    @app_commands.command(name="stats")
    async def slash_dnd_stats(self, interaction: discord.Interaction) -> None:
        """Roll 4d6 drop lowest for D&D PC stats"""
        rolls = sorted([sum(sorted([random.randint(1, 6) for x in range(4)])[1:]) for y in range(6)])
        await interaction.response.send_message(", ".join([str(i) for i in rolls]), ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MyCog(bot))
    # or if you want guild/guilds only...
    # await bot.add_cog(MyCog(bot), guilds=[discord.Object(id=...)])
