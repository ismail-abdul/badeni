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

'''
ConnectionCog
PlaybackCog
SeekCog
SearchCog
DBCog
'''

class Playback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # other inherited information
        # playback shouldn't need access to the queue. I only want play, pause, seek mb

    
    @nextcord.slash_command(description="Pauses playback.", guild_ids=[TESTING_GUILD_ID])
    async def pause(self, interaction: nextcord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        vc: VoiceClient | None = None
        try:
            vc = interaction.guild.voice_client #type: ignore
            assert (vc != None)
        except Exception as e:
            await interaction.send("badeni experienced an unforseen error")
            print(e)
            return
        
        if vc.is_playing():
            vc.pause()
            await interaction.send("resuming now")
        else:
            await interaction.send("nothing is playing?")

    @nextcord.slash_command(description="Resumes playback", guild_ids=[TESTING_GUILD_ID])
    async def resume(self, interaction: nextcord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        vc : VoiceClient | None = None
        try:
            vc = interaction.guild.voice_client #type: ignore
            assert (vc != None)
        except Exception as e:
            await interaction.send("badeni experienced an unforseen error")
            print(e)
            return
        
        if vc.is_paused:
            vc.resume()
            await interaction.send("resuming it now")
        else:
            await interaction.send("there's nothing to pause.")
        
