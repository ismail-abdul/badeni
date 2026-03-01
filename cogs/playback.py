import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member, SlashOption
import dotenv
from typing import List, Dict, Any, Optional, Union
import asyncio
from services.queue import Queue
from services.queueNode import QueueNode
from cogs.playerQueue import PlayerQueue
import os

# Load .env config
dotenv.load_dotenv()
config = dotenv.dotenv_values()
token = config['DISCORD_BOT_TOKEN']
test_guild_id = config["TESTING_GUILD_ID"]
assert(token != None)
assert(test_guild_id != None)
TESTING_GUILD_ID = int(test_guild_id)  # Make sure this is an int

class Playback(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        # other inherited information
        # playback shouldn't need access to the queue. I only want play, pause, seek mb
    
    async def is_vc_connected(self, interaction: Interaction):
        vc : VoiceClient = interaction.guild.voice_client #type: ignore
        if vc == None or  not vc.is_connected():
            await interaction.send("Not connected to any voice channel")
            return False
        return True
    
    @nextcord.slash_command(name="play_test", description="Test the ability of bot to play a piece of audio.", guild_ids=[])
    async def play_test_cmd(self, interaction: Interaction):
        await self.bot.defer(interaction) #type: ignore
        # exemplar filepath
        path = rf"..\songs\Aizpvina1Fs.opus"
        source: FFmpegOpusAudio = FFmpegOpusAudio(source=path)
        vc : VoiceClient = interaction.guild.voice_client #type: ignore
        if not self.is_vc_connected(interaction): return

        await asyncio.sleep(0.5)
        vc.stop()
        await asyncio.sleep(0.5)
        vc.play(source, after = self.placeholder_after(interaction))
        await interaction.send("Should be playing the track now.")
    
    
    @nextcord.slash_command(name="pause", description="Pauses a track if it's playing")
    async def pause(self, interaction: Interaction):
        await self.bot.defer(interaction) #type: ignore
        if not self.is_vc_connected(interaction): return
        vc : VoiceClient = interaction.guild.voice_client # type: ignore
        message = "paused"
        if vc.is_playing():
            vc.resume()
        else:
            message = "Nothing was playing"
        await interaction.send(message)
    
    @nextcord.slash_command(name="resume", description="Pauses a track if it's playing")
    async def resume(self, interaction: Interaction):
        await self.bot.defer(interaction) #type: ignore
        if not self.is_vc_connected(interaction): return
        vc : VoiceClient = interaction.guild.voice_client # type: ignore
        message = "resumed"
        if vc.is_paused():
            vc.resume()
        else:
            message = "Nothing was playing"
        await interaction.send(message)
    

    """
    A prototype for a flexible "play" that will enable users to search & enqueue or just straight up play a song.
    Decoupled from Discord's logic. 
    NOTE - What if the user simply wants to play a specific song immediately without interfacing with the queue. Is there a non-technical method of doing this? I don't want to force another slash option. Maybe there should be a play, enqueue and play now 
    """
    @nextcord.slash_command(name="play", description="Find & play specified track", guild_ids=[])
    async def play_cmd(self, interaction: Interaction, q: str = SlashOption(name="query")):
        await self.bot.defer(interaction) #type: ignore
        # should be able to search (later)

        # exemplar filepath
        path = rf"..\songs\Aizpvina1Fs.opus"

        # Validate the filepath.
        if not os.path.exists(path):
            await interaction.send("File doesn't exist")
            return
        
        # Update the queue
        pq: PlayerQueue | None = self.bot.get_cog("PlayerQueue") # type: ignore
        if pq == None:
            await interaction.send("testing: PlayerQueue cog is **disabled**.\nuser: queuing is currently disabled")
            return
        
        # NOTE - Access cog's enqueue slash command, which alters the 
        node = QueueNode(artist="Skepta, PlaqueboyMax", title="LESS IS MORE", length=200, source=FFmpegOpusAudio(source=path), path=path)
        if pq.enqueue_cmd(interaction, node=node) == False:
            pass
        await pq.queue_state_cmd(interaction)

    def placeholder_after(self, interaction):
        async def func(error: Exception | None):
            vc: VoiceClient = interaction.guild.voice_client # type: ignore
            if error:
                if vc.is_playing(): vc.pause()
                print(error)
                await vc.disconnect()
                await interaction.send("Error occurred")
            else:
                await interaction.send("Stream ended")
        
        return func
    
    #====================== Cog Lifecycle Management =======================================#
    # NOTE - Implement this when cog is complete.
    def cog_unload(self) -> None:
        pass
     