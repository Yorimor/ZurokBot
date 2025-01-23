import logging
from typing import Union

import discord
from discord.ext import commands
from discord.ext.commands import Context
import random
import _string

from mongoengine import QuerySet

from database.db import Quote

end_punctuation = "!?."


class Quotes(commands.Cog):
    """Quoting commands"""
    def __init__(self, bot):
        self.bot = bot

        self.quotes_used_cache = {}

    @commands.command()
    async def quote(self, ctx: Context, *args):
        """?quote - to get a random quote
        ?quote @mentions - to get a random quote containing the mentioned people
        ?quote @mention <quote> - quote a single user
        ?quote @mention <quote> @mention <quote> etc. - quote a group of users
        """
        msg = "If you can read this, something went wrong!"
        added_quote = False

        if len(args) == 0:
            # random quote from server members
            members = [m async for m in ctx.guild.fetch_members()]
            random.shuffle(members)

            for member in members:
                possible_quotes = Quote.objects(users__contains=str(member.id), enabled=True)
                if possible_quotes.count() == 0:
                    continue

                chosen_quote = possible_quotes[self.random_quote(possible_quotes.count(), mentions=[ctx.guild])]
                logging.info(f"Quote<{chosen_quote.id}> chosen from server {ctx.guild.name}")
                msg = self.format_quote(ctx, chosen_quote.quotes, chosen_quote.users)
                break

        elif len(set(args)) == len(ctx.message.mentions):
            # random quote that contains all mentioned users
            mentions = [mention for mention in ctx.message.mentions]
            print(mentions)

            possible_quotes = Quote.objects(users__contains=str(mentions[0].id), enabled=True)
            for mention in mentions[1:]:
                possible_quotes = possible_quotes.filter(users__contains=str(mention.id), enabled=True)

            count = possible_quotes.count()

            if count > 0:
                chosen_quote: Quote = possible_quotes[self.random_quote(possible_quotes.count(), mentions)]

                logging.info(f"Quote<{chosen_quote.id}> chosen from mentions {[(m.display_name, m.id) for m in mentions]}")
                msg = self.format_quote(ctx, chosen_quote.quotes, chosen_quote.users)
            else:
                msg = f"No quotes found for {'that user' if len(mentions) == 1 else 'those users'}!"

        else:
            # add quote
            mentions = [mention for mention in ctx.message.mentions]
            error = None

            quote_parts = {}
            current = 0
            for i, arg in enumerate(args):
                part = quote_parts.get(current, [[], ""])
                if arg.startswith("<@"):
                    if i != 0 and arg != part[1]:
                        current += 1

                    part = quote_parts.get(current, [[], ""])
                    part[1] = arg

                else:
                    if i == 0:
                        error = "First part is not a mention!"
                        break
                    part[0].append(arg)

                quote_parts[current] = part

            if error is None:
                for part in quote_parts.values():
                    if "&" in part[1]:
                        error = f"A role was mentioned instead of a user!"

                    elif len(part[0]) == 0:
                        user = self.mention_str_to_id(part[1])
                        error = f"{self.id_to_username(ctx, user)} was mentioned without any quote parts!"

            if error is not None:
                msg = f"Error: {error}"

            else:
                q = Quote(
                    quotes=[self.quote_str_from_parts(part[0]) for part in quote_parts.values()],
                    users=[self.mention_str_to_id(part[1]) for part in quote_parts.values()],
                    guild_id=str(ctx.guild.id),
                    channel_id=str(ctx.channel.id),
                    message_id=str(ctx.message.id),
                    dt=ctx.message.created_at,
                    added_by=str(ctx.message.author.id)
                ).save()
                msg = "*Quote added:*\n" + self.format_quote(ctx, q.quotes, q.users)
                logging.info(f"Added quote in server {ctx.guild.name} for member ids: {[(m.display_name, m.id) for m in mentions]}")
                added_quote = True

        await ctx.send(msg)

    def format_quote(self, ctx: Context, quotes, users):
        msg_parts = []
        for q, u in zip(quotes, users):
            msg_parts.append(f"> {q} - *{self.id_to_username(ctx, u)}*")

        return "\n".join(msg_parts)

    @staticmethod
    def mention_str_to_id(mention_str: str) -> str:
        m = mention_str[2:-1]
        if not m[1].isdigit():
            m = m[1:]
        return m

    @staticmethod
    def id_to_username(ctx, id_str: str) -> str:
        user = ctx.guild.get_member(int(id_str))
        if user is not None:
            return user.display_name
        return "Unknown User"

    @staticmethod
    def quote_str_from_parts(parts: list[str]) -> str:
        q = " ".join(parts)
        q = q[0].upper() + q[1:]

        if q[-1] not in "!?.":
            q += "."

        return q

    def random_quote(self, quotes_len: int, mentions: list[Union[discord.Member, discord.Guild]]) -> int:
        m_hash = hash(str(sorted([x.id for x in mentions])))
        self.quotes_used_cache[m_hash] = self.quotes_used_cache.get(m_hash, [])

        recent_limit = min(quotes_len // 10, 25)
        if len(self.quotes_used_cache[m_hash]) < recent_limit:
            self.quotes_used_cache[m_hash] = self.quotes_used_cache[m_hash][:recent_limit]

        rand_index = random.choice([x for x in range(quotes_len) if x not in self.quotes_used_cache[m_hash]])
        self.quotes_used_cache[m_hash].insert(0, rand_index)

        return rand_index


async def setup(bot):
    await bot.add_cog(Quotes(bot))
