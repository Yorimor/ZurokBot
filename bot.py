from typing import Any

import discord
import logging
import sys
from discord.ext import commands
from discord.ext.commands import MinimalHelpCommand, DefaultHelpCommand
from config import load_config, BotConfig
from logging.handlers import TimedRotatingFileHandler

from database.db import CmdUse

logging.basicConfig(
    level=logging.INFO,
    datefmt="%d/%m/%Y %H:%M:%S",
    format="{asctime} [{levelname:<7}][{filename:<10}->{funcName:>18}]: {message}",
    style="{",
    handlers=[
        # logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w"),
        TimedRotatingFileHandler(filename=f"logs/discord.log", when="midnight", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

cogs = [
    "dev",
    "quotes",
    "dnd",
    "misc",
    "dice",
    "wordle",
    "slash"
]


class Zurok(commands.Bot):
    """Zur'ok, First of his name, Shackler of Eternities, Roller of Dice, Scholar of the Sacred Quotes."""
    cfg: BotConfig
    version: str

    def __init__(self, config: BotConfig, intents: discord.Intents, **kwargs):
        super().__init__(command_prefix=config.prefix, intents=intents, **kwargs)

        self.cfg = config
        v = self.cfg.version
        self.version = f"v{v.major} \"{v.code}\""
        if v.minor > 0:
            self.version += f" update {v.minor}"

        if config.version.dev:
            self.version += " (Development Build)"

        self.activity = discord.CustomActivity(name="zurok.net", state="zurok.net")

    async def setup_hook(self):
        for cog in cogs:
            await self.load_extension(f"cogs.{cog}")
            logging.info(f"Cog <{cog}> loaded!")

    async def on_ready(self):
        logging.info(f"Logged in as {client.user} {self.version}")
        await self.tree.sync()

    async def on_message(self, message):
        if message.content.startswith(self.command_prefix):
            if message.author.bot:
                return  # ignore bot messages

            logging.info(f"Command: {message.content} - {message.author.name}/({message.author.id})")
            await self.process_commands(message)

    async def on_command_completion(self, ctx):
        if not self.cfg.version.dev or True:
            cmd_use = CmdUse(
                user_id=str(ctx.message.author.id),
                message_id=str(ctx.message.id),
                channel_id=str(ctx.message.channel.id),
                guild_id=str(ctx.message.guild.id),
                content=ctx.message.content,
                dt=str(ctx.message.created_at)
            )
            cmd_use.save()


class ZurokHelp(MinimalHelpCommand):

    def __init__(self, **options: Any):
        super().__init__(**options)


if __name__ == "__main__":
    # bot_intents = discord.Intents.all()
    # bot_intents.message_content = True

    bot_name = sys.argv[1]
    cfg, token = load_config(bot_name)

    help_cmd = MinimalHelpCommand(show_parameter_descriptions=False)
    # help_cmd = DefaultHelpCommand(show_parameter_descriptions=False)

    client = Zurok(config=cfg, intents=discord.Intents.all(), help_command=help_cmd)
    client.run(token, log_handler=None)
