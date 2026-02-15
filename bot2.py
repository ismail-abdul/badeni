import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member
import dotenv
import logging
import random
from Queue import Queue
from QueueNode import QueueNode
from typing import List, Dict, Any, Optional, Union
import asyncio
import yt_dlp
import os
import sqlite3

from cogs.playback import Playback 
from cogs.playerQueue import PlayerQueue
from cogs.voice import Voice
from cogs.search import Search

# Logging
logger = logging.getLogger('nextcosrd')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Load .env config
dotenv.load_dotenv()
config = dotenv.dotenv_values()
token = config['DISCORD_BOT_TOKEN']
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
queue: Queue = Queue(limit=20)

# Bot & gateway intents setup.
intents = nextcord.Intents.default()
bot = commands.Bot(intents=intents)

playback = Playback(bot=bot)
player_q = PlayerQueue(bot=bot, queue=queue, audio_ydl=audio_ydl)
voice = Voice(bot=bot, conn=conn, cur=cur, audio_ydl=audio_ydl, search_ydl=search_ydl, queue=queue)
search = Search(bot=bot,audio_ydl=audio_ydl, search_ydl=search_ydl)
bot.add_cog(playback, override = True)
bot.add_cog(player_q, override = True)
bot.add_cog(voice, override = True)
bot.add_cog(search, override = True)

bot.run(token)


