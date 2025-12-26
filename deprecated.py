import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member
import dotenv
import logging
import random
import subprocess
from Queue import Queue
from QueueNode import QueueNode
from typing import List, Dict, Any, Optional, Union
import asyncio
import yt_dlp
import sqlite3

class Deprecated(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    '''
        Generates a yt-dlp subprocess that searches Youtube. Then returns the data specifed by the --print arguments.
        @param search_inp is searched for in Youtube
        @param result_count number results extracted from the YT search.
        @param args the field data to be extracted. Arguments be found in the OUTPUT TEMPLATE part of the github repo's README.

        @return A dict of the form {arg: value}. e.g. {'artist': 'PlaqueBoyMax, Skepta, 5STAR'}

        @raise subprocess.CalledProcessError if an error occurs within the yt-dlp subprocess
        I wish args and kwargs were ideal here. I want an excuse to use them in a function. 
        Acc I could, but then we taking up double memory unecessarily (asymptotically of course).
    '''
    async def get_audio_subprocess(self, form: str, url: str):
        completed_process = subprocess.run(
            args=['yt-dlp.exe', '-x', '-gw', '--audio-format', form, url],
            capture_output=True,
            text=True,
            timeout=30
        )
        return completed_process