import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member
from typing import List, Dict, Any, Optional, Union
import yt_dlp
import asyncio

"""
Commands and methods related to searching local and web-based
sources of music.

Returning search results, paths, fields from a database. 
"""

class Search(commands.Cog):
    DEFAULT_PRINT_FIELDS =  ('artist','webpage_url','title')
    EMOJI_TO_NUMBER = {
        "1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5,
        "6️⃣": 6, "7️⃣": 7, "8️⃣": 8, "9️⃣": 9, "🔟": 10
    }
    NUMBER_TO_EMOJI = {v:k for k,v in EMOJI_TO_NUMBER.items()}

    def __init__(self, bot: nextcord.Client, audio_ydl: yt_dlp.YoutubeDL, search_ydl: yt_dlp.YoutubeDL):
        self.bot = bot
        self.audio_ydl = audio_ydl
        self.search_ydl = search_ydl

    
    