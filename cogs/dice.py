from discord.ext import commands
from discord.ext.commands import Context
import dice


class Dice(commands.Cog):
    """Dice rolling commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll", aliases=["r", "dice"])
    async def _roll(self, ctx: Context, *rolls):
        """Roll dice using 1d6 dice notation!"""
        results = []
        for roll in rolls:
            result = dice.roll(roll)
            if isinstance(result, list):
                result = sum(result)

            results.append(f"`{roll}`: {result}")

        await ctx.send("**Results**\n" + "\n".join(results))



async def setup(bot):
    await bot.add_cog(Dice(bot))
