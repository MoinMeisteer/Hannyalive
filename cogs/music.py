import discord
import yt_dlp as youtube_dl
import asyncio
import datetime
import db
from db import insert_song, get_song_by_url
from cogs.config import logger, setup_logger

music_logger = setup_logger('music')

playlists = {}
song_queue = asyncio.Queue()
player = None

class YTDLSource(discord.PCMVolumeTransformer):
    yt_dlp_options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': False,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }

    ytdl = youtube_dl.YoutubeDL(yt_dlp_options)

    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.id = data.get('id')
        print(f"YTDLSource initialized with ID: {self.id}")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, start_time=None):
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(url, download=not stream))
        except Exception as e:
            print(f"Error extracting info: {e}")
            return None

        if data is None:
            return None

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else cls.ytdl.prepare_filename(data)
        ffmpeg_opts = cls.ffmpeg_options.copy()
        if start_time:
            ffmpeg_opts['options'] += f' -ss {start_time}'
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_opts), data=data)


async def play_song(guild, url, channel, bot, control_view):
    global player
    global playlists, song_queue
    global current_song, current_song_length, current_song_start_time

    async with channel.typing():
        try:
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            voice_client = guild.voice_client
            if not voice_client:
                channel = guild.voice_channels[3]
                voice_client = await channel.connect()

            if voice_client.is_playing():
                await song_queue.put(player)
                await channel.send(f'**{player.title}** zur Warteschlange hinzugefügt.')
            else:
                voice_client.play(player, after=lambda e: on_song_end(guild, player.id))
                current_song = player.title
                current_song_length = player.duration
                current_song_start_time = datetime.datetime.utcnow()
                await channel.send(
                    f'Jetzt spielt: **{player.title}** (Dauer: {datetime.timedelta(seconds=player.duration)})',
                    view=control_view)
                db.insert_song(player.url, player.title, player.duration)
                db.increment_play_count(player.id)  # Hier wird die Abspielanzahl erhöht
        except Exception as e:
            await channel.send(f'Fehler beim Abspielen des Liedes: {e}')
            logger.error(f'Fehler beim Abspielen des Liedes: {e}')

def on_song_end(error, guild, control_view):
    if error:
        print(f'Player error: {error}')
    # Fügen Sie hier die Logik hinzu, die beim Beenden eines Songs ausgeführt werden soll
    print(f'Song {current_song} ist zu Ende gespielt.')

async def get_current_song(guild):
    voice_client = guild.voice_client
    if voice_client and voice_client.is_playing():
        player = voice_client.source
        if isinstance(player, YTDLSource):
            return player.title
    return "Kein Song wird abgespielt"
