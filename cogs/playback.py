import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member
import dotenv
from typing import List, Dict, Any, Optional, Union
import asyncio

# Load .env config
dotenv.load_dotenv()
config = dotenv.dotenv_values()
token = config['DISCORD_BOT_TOKEN']
test_guild_id = config["TESTING_GUILD_ID"]
assert(token != None)
assert(test_guild_id != None)
TESTING_GUILD_ID = int(test_guild_id)  # Make sure this is an int

class Playback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # other inherited information
        # playback shouldn't need access to the queue. I only want play, pause, seek mb

    
