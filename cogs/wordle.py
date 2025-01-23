import asyncio
import logging
from mongoengine import NotUniqueError
from discord import Message
from discord.ext import commands, tasks
from discord.ext.commands import Context
from database.db import WordleGame
from wordle.solver import WordleSolver
from datetime import time, datetime

# WORDLE_CHANNEL = 932424557397160066
WORDLE_CHANNELS = [943296571209039903, 932424557397160066]
DEV_CHANNEL = 426871841764802560


class Wordle(commands.Cog):
    """Wordle stats!!!!"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.cfg.version.dev:
            self.wordle_ch = DEV_CHANNEL
        else:
            self.wordle_ch = WORDLE_CHANNELS[0]

        self.solver = WordleSolver()

        self.play_hour = 15

    async def cog_load(self) -> None:
        # start the task to run in the background
        # self.play_wordle_task.start()
        pass

    @tasks.loop(hours=1)
    async def play_wordle_task(self):
        now = datetime.now()
        if now.hour == self.play_hour:
            logging.info("Wordle time!")
            channel = await self.bot.fetch_channel(self.wordle_ch)
            game = self.solver.play()
            if game is not None:
                await channel.send(game[1])
            else:
                logging.info("Wordle solve failed.")

    @play_wordle_task.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()  # wait until the bot logs in

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.channel.id in WORDLE_CHANNELS:
            r = self.process_wordle_message(message)
            if r:
                logging.info(f"Wordle {r.game} saved from wordle channel!")

    @commands.group(hidden=True)
    @commands.is_owner()
    async def wordle(self, ctx):
        if ctx.invoked_subcommand is None:
            """Play wordle!"""
            game = self.solver.play()
            if game is not None:
                await ctx.send(game[1])

    @wordle.command(hidden=True)
    @commands.is_owner()
    async def fetch(self, ctx: Context):
        """Fetch all the wordle games from the wordle channel"""
        for channel in WORDLE_CHANNELS:
            wordle_ch = await self.bot.fetch_channel(channel)

            logging.info(f"Fetching wordle messages from {channel}...")
            count = 0
            async for message in wordle_ch.history(limit=5000):
                r = self.process_wordle_message(message)
                if r:
                    count += 1

                    if count % 20 == 0:
                        logging.info(count)

            logging.info(f"Done! {wordle_ch.display_nam}")

    def process_wordle_message(self, message: Message):
        if not message.content.startswith("Wordle"):
            return False

        _w, game, score = message.content.split("\n")[0].split(" ")
        hard_mode = False
        if "*" in score:
            hard_mode = True

        if score[0] == "X":
            score = 7
        else:
            score = int(score[0])

        game = int(game)

        wordle_tiles = ["⬛", "🟨", "🟩"]

        msg = message.content.replace("⬜", "⬛")

        lines = msg.split("\n")
        guesses = []
        for line in lines:
            if line.startswith("⬛") or line.startswith("🟨") or line.startswith("🟩"):
                guesses.append("".join([x for x in line if x in wordle_tiles]))

        if WordleGame.objects(user_id=str(message.author.id), game=game).count() == 0:
            wg = WordleGame(
                user_id=str(message.author.id),
                msg_id=message.id,
                game=game,
                score=score,
                hard_mode=hard_mode,
                msg_content=message.content,
                guesses=guesses
            )
            wg.save()
            return wg

        return False


async def setup(bot):
    await bot.add_cog(Wordle(bot))
