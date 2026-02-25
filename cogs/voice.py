import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member
from typing import List, Dict, Any, Optional, Union
from bot import Badeni

class Voice(commands.Cog):
    def __init__(self, bot: Badeni):
        self.bot = bot
    

    """When bot is ready to communicate on Discord, 
    amessage is outputed to command line. """
    @commands.Cog.listener()
    async def on_ready(self):
        connections = self.bot.voice_clients
    
        for vc in connections:
            await vc.disconnect(force=True)
        
        print(f'We have logged in as {self.bot.user}')
    
    # When bot goes offline and completely disconnects from discord.
    @commands.Cog.listener()
    async def on_disconnect(self):
        connections = self.bot.voice_clients
    
        for vc in connections:
            await vc.disconnect(force=True)
        
        self.cur.close()
        self.conn.close()
        self.audio_ydl.close()
        self.search_ydl.close()
    
    
        print("The bot disconnected fr. Should also disconnect voice connections everywhere.\n")
    
    # Called when a Member changes their VoiceState. 
    # In our case, we are using it to check for bot inactivity.
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState, active: bool = False):
        if not active:
            return
        
        print(f'\nThere was a state change.')
        
        if self.bot.user == None:
            return
        if member.id != self.bot.user.id: # check that member is our bot
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

    #====================== Cog Lifecycle Management =======================================#
    # NOTE - Implement this when cog is complete. 
    def cog_unload(self) -> None:
        pass

    
    #======================== Connection Commands & Logic ================================#

    @nextcord.slash_command(name="join", description="Join current voice channel", guild_ids=[])
    async def join(self, interaction: Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True,with_message=True)
    
        #identify user voice state
        botVoiceClient: VoiceClient | None = interaction.guild.voice_client # type: ignore
        userVoiceState = interaction.user.voice #type: ignore
    
        # print(f"Active voice clients: {bot.voice_clients}")
        for vc in self.bot.voice_clients:
            print('Disconnecting old voice clients')
            await vc.disconnect(force=True)
    
        if (userVoiceState == None):
            await interaction.followup.send("not in a voice channel")
            return 
        elif (botVoiceClient and botVoiceClient.channel == userVoiceState.channel):
            # What if you don't want users to move the bot relentessly
            await interaction.followup.send("bot already connected to this channel")
            return
    
        channel = userVoiceState.channel
        try:
            await channel.connect(reconnect=False, timeout=10) #type: ignore
        except Exception as exception:
            vc = interaction.guild.voice_client # type: ignore
            if vc:
                print("Error in connecting to channel. Disconnecting guild's voice client.")
                await vc.disconnect(force=True)
    
            await interaction.followup.send("Error in joining")
            print(exception)
            return
        
        await interaction.followup.send("should join now")
    
    # Need to add null_safety.
    @nextcord.slash_command(name="leave", description="Leave the current voice channel.", guild_ids=[])
    async def leave(self, interaction: Interaction):    
        try:
            # Access the existing cogs
            vc: VoiceClient = interaction.guild.voice_client # type: ignore
            await vc.disconnect(force=True)
            self.queue.clear()
            await interaction.send("bot has left")
        except:
            if not interaction.guild:
                await interaction.send("command not sent from a guild")
            elif not interaction.guild.voice_client:
                await interaction.send("bot not connected to any voice channels")
            elif not interaction.user:
                await interaction.send("command not sent by a user")
            elif not interaction.user.voice: #type: ignore
                await interaction.send("you are not in a voice channel")
        finally:
            return
        

    