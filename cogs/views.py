from typing import Any

import discord
from discord import Interaction
from discord._types import ClientT
from discord.ext import commands
from discord.ui import Button, View
from cogs.music import play_song, get_current_song, song_queue
import datetime
import asyncio
import logging
from db import get_song_history, get_all_songs, get_song_by_url


from cogs.config import logger, setup_logger


logger = logging.getLogger('views')



class PlayButton(Button):
    def __init__(self, control_view, bot):
        super().__init__(label="Play", style=discord.ButtonStyle.green, emoji="▶️")
        self.control_view = control_view
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Bitte gib die URL des Songs ein:", ephemeral=True)
        logger.error("Music url is None")
        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        try:
            message = await self.bot.wait_for('message', check=check, timeout=30.0)
            url = message.content.strip()
            await interaction.followup.send(f'Spiele den Link "{url}" ab...', ephemeral=True)
            await play_song(interaction.guild, url, interaction.channel, self.bot, self.control_view)
        except asyncio.TimeoutError:
            await interaction.followup.send('Zeit abgelaufen. Bitte versuche es erneut.', ephemeral=True)
        except Exception as e:
            logger.error(f'Error handling PlayButton interaction: {e}')
            await interaction.followup.send(f'Fehler beim Abspielen des Liedes: {e}', ephemeral=True)

class PlayFromDBButton(Button):
    def __init__(self, control_view, bot):
        super().__init__(label="Play from DB", style=discord.ButtonStyle.green, emoji="▶️")
        self.control_view = control_view
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        songs = get_all_songs()
        for song in songs:
            url, title, duration = song
            await play_song(interaction.guild, url, interaction.channel, self.bot, self.control_view)



class PauseButton(Button):
    def __init__(self):
        super().__init__(label="Pause", style=discord.ButtonStyle.gray, emoji="⏸️")

    async def callback(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("Lied pausiert.", ephemeral=True)
        elif voice_client and voice_client.is_paused():
            await interaction.response.send_message("Das Lied ist bereits pausiert.", ephemeral=True)
        else:
            await interaction.response.send_message("Es wird kein Lied abgespielt.", ephemeral=True)


class ResumeButton(Button):
    def __init__(self):
        super().__init__(label="Resume", style=discord.ButtonStyle.green, emoji="▶️")

    async def callback(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("Wiedergabe fortgesetzt.", ephemeral=True)
        elif voice_client and voice_client.is_playing():
            await interaction.response.send_message("Die Wiedergabe läuft bereits.", ephemeral=True)
        else:
            await interaction.response.send_message("Es wird kein Lied pausiert.", ephemeral=True)


class JoinButton(Button):
    def __init__(self):
        super().__init__(label="Join", style=discord.ButtonStyle.green, emoji="🔊")

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        if user:
            voice_state = user.voice
            if voice_state and voice_state.channel:
                channel = voice_state.channel
                if not interaction.guild.voice_client:
                    await channel.connect()
                    await interaction.response.send_message(f"Bot ist dem Sprachkanal {channel.name} beigetreten.",
                                                            ephemeral=True)
                else:
                    await interaction.response.send_message(f"Bot ist bereits im Sprachkanal {channel.name}.",
                                                            ephemeral=True)
            else:
                await interaction.response.send_message("Du bist nicht in einem Sprachkanal.", ephemeral=True)
        else:
            await interaction.response.send_message("Benutzerinformationen konnten nicht abgerufen werden.",
                                                    ephemeral=True)


class SkipButton(Button):
    def __init__(self):
        super().__init__(label="Skip", style=discord.ButtonStyle.red, emoji="⏭️")

    async def callback(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            if song_queue.empty():
                await interaction.response.send_message("Die Warteschlange ist leer.", ephemeral=True)
            else:
                next_song = await song_queue.get()
                voice_client.stop()  # Stoppe das aktuelle Lied
                voice_client.play(next_song, after=lambda e: print(f'Player error: {e}') if e else None)
                await interaction.response.send_message(
                    f'Jetzt spielt: **{next_song.title}** (Dauer: {datetime.timedelta(seconds=next_song.duration)})',
                    ephemeral=True)
        else:
            await interaction.response.send_message("Es wird kein Lied abgespielt, das übersprungen werden könnte.",
                                                    ephemeral=True)


class LeaveButton(Button):
    def __init__(self):
        super().__init__(label="Leave", style=discord.ButtonStyle.red, emoji="👋")

    async def callback(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client:
            await voice_client.disconnect()
            await interaction.response.send_message("Ich bin raus Ciao.", ephemeral=True)
        else:
            await interaction.response.send_message("Bot ist nicht in einem Sprachkanal.", ephemeral=True)


class HistoryButton(discord.ui.Button):
    def __init__(self, control_view, bot):
        super().__init__(label="History", style=discord.ButtonStyle.blurple, emoji="📜")
        self.control_view = control_view
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
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

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Fehler beim Anzeigen der Song-History: {e}")
            await interaction.response.send_message("Es ist ein Fehler beim Anzeigen der Song-History aufgetreten.", ephemeral=True)



class ControlView(View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.add_item(PlayButton(self, bot))
        self.add_item(PauseButton())
        self.add_item(ResumeButton())
        self.add_item(SkipButton())
        self.add_item(JoinButton())
        self.add_item(LeaveButton())
        self.add_item(HistoryButton(self, bot))
        self.add_item(PlayFromDBButton(self, bot))

    async def send_with_history(self, interaction: discord.Interaction):
        songs = get_song_history()
        song_list = []
        for i, song in enumerate(songs, 1):
            title, duration = song
            formatted_song = f"{i}. **{title}** - {str(datetime.timedelta(seconds=duration))}"
            if len("\n".join(song_list)) + len(formatted_song) > 4000:
                break
            song_list.append(formatted_song)

        if len(song_list) >= 25:
            song_list = song_list[:25]
            song_list.append("... (weitere Einträge wurden ausgelassen)")

        song_list_str = "\n".join(song_list)
        embed = discord.Embed(
            title='History of Played Songs',
            description=song_list_str,
            color=discord.Color.blue()
        )

        await interaction.response.send_message(embed=embed, view=self, ephemeral=True)


class PositionalPlayButton(Button):
    def __init__(self, song_id, label, bot, control_view):
        super().__init__(label=label, style=discord.ButtonStyle.green, emoji="▶️")
        self.song_id = song_id
        self.bot = bot
        self.control_view = control_view

    async def callback(self, interaction: discord.Interaction):
        song = db.get_song_by_id(self.song_id)
        if song:
            url, title, duration, play_count = song
            await interaction.response.send_message(f'Spiele "{title}" ab...', ephemeral=True)
            await play_song(interaction.guild, url, interaction.channel, self.bot, self.control_view)
        else:
            await interaction.response.send_message('Song nicht gefunden.', ephemeral=True)


class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def menu(self, ctx):
        control_view = ControlView(self.bot)
        await control_view.send_with_history(ctx.interaction)


