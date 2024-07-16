import asyncio

import discord
from discord.ext import commands


from cogs.views import ControlView, MyCog
from cogs.commands import setup_commands
import datetime
from settings import bot
import logging
from cogs.config import DISCORD_TOKEN
from cogs.config import logger, setup_logger
from db import get_song_history, get_all_songs



bot.start_time = datetime.datetime.utcnow()





async def load_extensions():
    extensions = [
        'cogs.music',
        'cogs.config2',
        'cogs.views',
        'cogs.commands',
        'cogs.history',
        'cogs.settings'
    ]

    for ext in extensions:
        try:
            await bot.load_extension(ext)
            logger.info(f'Loaded extension {ext}')
        except Exception as e:
            logger.error(f'Failed to load extension {ext}: {e}')

setup_commands(bot)

ERROR_LOG_CHANNEL_ID = 1262533134155518022

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


bot.add_cog(MyCog(bot))

@bot.command(name='menu')
async def menu(ctx):
    try:
        songs = get_all_songs()

        if not songs:
            song_list_str = "Es gibt keine Songs in der Datenbank."
        else:
            song_list = []
            for i, (url, title, duration, play_count) in enumerate(songs):
                formatted_song = f"{i+1}. **{title}** - {str(datetime.timedelta(seconds=duration))} ({play_count} mal abgespielt)"
                song_list.append(formatted_song)

            song_list_str = "\n".join(song_list)

        embed = discord.Embed(
            title='History of Played Songs',
            description=song_list_str,
            color=discord.Color.blue()
        )

        control_view = ControlView(bot)
        await ctx.send(embed=embed, view=control_view)

    except Exception as e:
        logger.error(f"Fehler beim Anzeigen der Song-History: {e}")
        await ctx.send("Es ist ein Fehler beim Anzeigen der Song-History aufgetreten.")


@bot.event
async def on_ready():
    bot.start_time = datetime.datetime.utcnow()
    logger.info(f'Erfolgreich eingeloggt {bot.user}')


async def main():
    await load_extensions()
    await bot.start(DISCORD_TOKEN)


if __name__ == '__main__':
    asyncio.run(main())