from discord.ext.commands import Context


async def is_owner(ctx: Context):
    return ctx.author.id == 214497342844305410
