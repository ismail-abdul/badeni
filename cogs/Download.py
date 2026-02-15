import nextcord.ext.commands as commands

from yt_dlp import YoutubeDL


class Download(commands.Cog):
    def __init__(self, audio_ydl : YoutubeDL):
        self.audio_ydl = audio_ydl
    
    """
    Responsible for downloading songs from the web. 
    Purely for downloads. No searching. Just take in a link,
    download or fail. Return paths and audio_sources etc. 

    Should also have functions to pull from local database.
    """
