import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member
import dotenv
import logging
import random
from services.Queue import Queue
from services.QueueNode import QueueNode
from typing import List, Dict, Any, Optional, Union
import asyncio
import yt_dlp
import os
import sqlite3

from cogs.Playback import Playback 
from cogs.PlayerQueue import PlayerQueue
from cogs.Voice import Voice
from cogs.Search import Search
from services.Search import Search as SearchService
from cogs.Data import Data

from cogs.helpers import streamEndsOrError

# Logging
logger = logging.getLogger('nextcosrd')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Load .env config
dotenv.load_dotenv()
config = dotenv.dotenv_values()
token: str = config['DISCORD_BOT_TOKEN'] # type: ignore
test_guild_id = config["TESTING_GUILD_ID"]
assert(token != None)
assert(test_guild_id != None)
TESTING_GUILD_ID = int(test_guild_id)  # Make sure this is an int
DEFAULT_PRINT_FIELDS =  ('artist','webpage_url','title')
EMOJI_TO_NUMBER = {
    "1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5,
    "6️⃣": 6, "7️⃣": 7, "8️⃣": 8, "9️⃣": 9, "🔟": 10
}
NUMBER_TO_EMOJI = {v:k for k,v in EMOJI_TO_NUMBER.items()}


# Databse setup.
conn, cur = None, None #type: ignore
try:
    conn: sqlite3.Connection = sqlite3.connect("songs.db")
    cur: sqlite3.Cursor = conn.cursor()
except:
    print("Failed to connect to database")
    try:
        conn.close()
        cur.close
    except:
        pass
    raise SystemExit

audio_ydl = yt_dlp.YoutubeDL({
    'format': 'opus/bestaudio',
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
    }],
    'outtmpl': './songs/%(id)s.%(ext)s'
}) # type: ignore
search_ydl = yt_dlp.YoutubeDL({})

# The queue contains the currently playing song.

# intents = nextcord.Intents.default()
# bot = commands.Bot(intents=intents)


"""
Mind that the Client is a class attribute in this case.
"""
class Badeni(commands.Bot):
    def __init__(self, queue: Queue = Queue(limit=10), search_service: SearchService = SearchService()):
        # Bot & gateway intents setup.
        intents = nextcord.Intents.default()
        super().__init__(
            intents=intents
        )

        # Create and attach cogs to bot.
        voice = Voice(self)
        playback = Playback(self)
        player_q = PlayerQueue(self, queue=queue)
        search = Search(self, search_service)

        self.add_cog(voice, override = True)
        self.add_cog(playback, override = True)
        self.add_cog(player_q, override = True)
        self.add_cog(search, override = True)
    """
    Defers the interaction if not already responded to.
    """
    async def defer(self, interaction: Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True, with_message=True)
        else:
            print(f'Interaction at {interaction.created_at} WAS NOT deferred.')
    
    async def on_ready(self):
        #Load media files from elsewhere
        connections = self.voice_clients
    
        for vc in connections:
            await vc.disconnect(force=True)
        
        print(f'We have logged in as {self.user}')
    
    # When bot goes offline and completely disconnects from discord.
    async def on_disconnect(self):
        connections = self.voice_clients
    
        for vc in connections:
            await vc.disconnect(force=True)
        
        # global conn
        # global cur
        # global audio_ydl
        # global search_ydl
        # cur.close()
        # conn.close()
        # audio_ydl.close()
        # search_ydl.close()
    
    
        print("The bot disconnected fr. Should also disconnect voice connections everywhere.\n")
    
    # Called when a Member changes their VoiceState. 
    # In our case, we are using it to check for bot inactivity.
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState, active: bool = False):
        if not active:
            return
        
        print(f'\nThere was a state change.')
        
        if self.user == None:
            return
        if member.id != self.user.id: # check that member is our bot
            return
        elif not member.voice:
            print("Bot has no voice state.")
            return
        elif not member.voice.channel: # Is the bot even in a channel.
            print("Bot isn't in a channel ??? I think...")
            return
        elif before.channel == None and after.channel != None: # Is it a join event.
            print("Bot is just joining")
            return
        elif before.channel == after.channel: # Is it just a reconnection thing?
            print("\n VoiceState Update: Could be a reconnection thing \n")
        elif member.guild.voice_client == None:
            # No voice client means no voide connection
            print('\n No VoiceClient for this guild at the moment\n')
        elif member.guild.voice_client.is_playing(): # type: ignore
            # check queue state. Is the player active // playing something?
            print("\n Big man ting, the bot is playing still\n")
            return
        else:
            print("Don't know exactly what it is yet.")
        print("\n")
        # TODO - Checks for the type of reaction given to a message (when called). Takes same arguements as the on_reaction_add event.
    
    def reaction_add_check(self, reaction: nextcord.Reaction, user: Union[nextcord.Member, nextcord.User]) -> bool:
        print("Checking if reaction is organic")
        emoji = reaction.emoji
        return not( user.bot and EMOJI_TO_NUMBER.get(emoji) ) #type: ignore
    

