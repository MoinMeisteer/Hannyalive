from discord.ext import commands
from cogs.views import ControlView
from cogs.music import playlists, play_song

def setup_commands(bot):
    #@bot.command(name='menu')
    #async def menu(ctx):
    #    await ctx.send("Wähle einen Befehl aus der Liste:", view=ControlView())

    @bot.command(name='add_to_playlist')
    async def add_to_playlist(ctx, playlist_name, url):
        if playlist_name in playlists:
            playlists[playlist_name].append(url)
            await ctx.send(f'**{url}** zur Playlist **{playlist_name}** hinzugefügt.')
        else:
            await ctx.send(f'Playlist **{playlist_name}** existiert nicht.')