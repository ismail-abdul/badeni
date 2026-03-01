import nextcord
import nextcord.ext.commands as commands
from nextcord import VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member
import dotenv
import logging
import random
from services.queue import Queue
from services.queueNode import QueueNode
from typing import List, Dict, Any, Optional, Union
import asyncio
import yt_dlp
import os
import sqlite3

from cogs.playback import Playback 
from cogs.playerQueue import PlayerQueue
from cogs.voice import Voice
from cogs.Search import Search
from services.Search import Search as SearchService
from cogs.Data import Data

from cogs.helpers import streamEndsOrError

# Logging
logger = logging.getLogger('nextcord')
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
        cur.close()
    except sqlite3.Error as e:
        print(e)
    raise SystemExit


class Badeni(commands.Bot):
    """
    Mind that the Client is a class attribute in this case.
    """
    def __init__(self, queue: Optional[Queue], search_service: SearchService = SearchService()):
        # Bot & gateway intents setup.
        intents = nextcord.Intents.default()
        super().__init__(
            intents=intents
        )
        queue = queue or Queue(limit=10)
        # Create and attach cogs to bot.
        voice = Voice(self)
        playback = Playback(self)
        player_q = PlayerQueue(self, queue=queue)
        search = Search(self, search_service)

        self.add_cog(voice, override = True)
        self.add_cog(playback, override = True)
        self.add_cog(player_q, override = True)
        self.add_cog(search, override = True)
    
    async def defer(self, interaction: Interaction):
        """Defers the interaction if not already responded to."""
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True, with_message=True)
        else:
            print(f'Interaction at {interaction.created_at} WAS NOT deferred.')
    
    def reaction_add_check(self, reaction: nextcord.Reaction, user: Union[nextcord.Member, nextcord.User]) -> bool:
        print("Checking if reaction is organic")
        emoji = reaction.emoji
        return not( user.bot and EMOJI_TO_NUMBER.get(emoji) ) #type: ignore
    

