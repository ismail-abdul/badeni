import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member
from typing import List, Dict, Any, Optional, Union
import asyncio
from Queue import *
import os
from yt_dlp import YoutubeDL


class PlayerQueue(commands.Cog):
    def __init__(self, bot, queue: Queue, audio_ydl: YoutubeDL):
        self.bot = bot
        self.queue = queue
        self.audio_ydl = audio_ydl
        self.DEFAULT_PRINT_FIELDS =  ('artist','webpage_url','title')
        self.EMOJI_TO_NUMBER = {
            "1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5,
            "6️⃣": 6, "7️⃣": 7, "8️⃣": 8, "9️⃣": 9, "🔟": 10
        }
        self.NUMBER_TO_EMOJI = {v:k for k,v in self.EMOJI_TO_NUMBER.items()}
    
    # Called when a stream ends or an error occurs.
    # can i pass an interaction? can I edit// override the function to take the interactionn
    # Supply an interaction to the finaliser funciton. I.e when the stream ends or an error occurs.
    # Read https://docs.nextcord.dev/en/stable/faq.html#how-do-i-pass-a-coroutine-to-the-player-s-after-function for info on how to properly do this.
    def streamEndsOrError(self, interaction: Interaction):
        """
        Using a higher order function provides context to func without breaking the defintion for after.
        Once called, this lower func with 'hidden' context is returned. 
        Hence, we have an finalizer function/coroutine with only error. In theory, 
        we could apply args and kwargs to this pattern.
        """
        async def func(error: Exception | None):
            global queue # type: Queue
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=False, with_message=True)
            vc: VoiceClient = interaction.guild.voice_client # type: ignore
    
            # i.e. connection loss, player fails to process audio, server fails etc. Need to handle each case seperately later.
            if error:
                if vc.is_playing():
                    vc.pause()
                await vc.disconnect()
                self.queue.clear()
                await interaction.send("Error whilst playing (queue cleared). Disconnecting voice client.")
                print(error)
                return 
            
            if self.queue.isEmpty:
                if vc.is_playing():
                    vc.pause()
                await vc.disconnect()
                await interaction.send("Stream ended. Disconnecting voice client.")
                return
            
            node: QueueNode = self.queue.dequeue()
            if vc.is_playing():
                vc.stop()
            vc.play(source=node.source, after = self.streamEndsOrError(interaction))
            await interaction.send('Playing the next song.') # Improve UX here. Need to make some cool embeds. Mb some templating can be created.
        
        return func
    
    #========================= Queue Management =========================================#
    
    @nextcord.slash_command(name="queue", description="See the current state of the queue.", guild_ids=[])
    async def queue_state_cmd(self, interaction: Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(with_message=True)
        # An embed with cool images and alll that would fit perfectly here.
        if self.queue.isEmpty:
            await interaction.send("queue is empty.")
        
        content='Current Queue: \n'
        for i in range(self.queue.length):
            node: QueueNode = self.queue.get(i)
            artist = node.artist
            title = node.title
            length = node.length
            url = node.url
            line = f'{i}. [{title}]({url}) - {artist} ({length})\n'
            content += line
        
        await interaction.send(content)
    
    @nextcord.slash_command(name="populate_q", description="Pre-populates queue w/ some hard-coded songs.", guild_ids=[])
    async def populate_q_cmd(self, interaction: Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=False, with_message=True)
        await self.populate_q(interaction)
        await interaction.send("finished pre-population")
        
        global queue
        vc: VoiceClient = interaction.guild.voice_client #type: ignore
        if not vc.is_playing():
            node: QueueNode = self.queue.get(0)
            vc.play(source=node.source, after=self.streamEndsOrError(interaction))
        
        await self.queue_state_cmd(interaction)
        
    
    async def populate_q(self, interaction: Interaction):
        # Manage queue. Take the url, download the file.
        yt_ids = [r"0DPNmsLrqFE", r"rKUJG5TdAl8", r"4QXXEUD9Kgc", r"0MT1AegYI_4", r"SfK549sa8VE"]
        for id in yt_ids:
            url = rf'www.youtube.com/watch?v={id}'
            path = rf'..\songs\{id}.opus'
            node = None
            if not os.path.exists(path):
                info = self.audio_ydl.extract_info(url, download=True)
                artist: str | None = info.get('uploader')
                title: str | None = info.get('title')
                source = FFmpegOpusAudio(path)
                node = QueueNode(artist=artist, length=0, source=source, url=url, title=title)
            else:
                source = FFmpegOpusAudio(f'songs/{id}.opus')
                node = QueueNode('N/A', 0, source, url, 0, id)
            self.queue.enqueue(node)
    
                
    
    
    @nextcord.slash_command(name="clear", description="Cleares the queue w/o skipping the current song", guild_ids=[])
    async def clear(self, interaction: Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        while self.queue.length > 1:
            self.queue.dequeue(1)
        await interaction.send("Queue has been cleared")
    
    @nextcord.slash_command(name="remove", description="Remove song from queue", guild_ids=[])
    async def remove(self, interaction: Interaction, choice: int = nextcord.SlashOption(name='choice')):
        # Send message with current queue state
        await self.queue_state_cmd(interaction)
        message = await interaction.original_message()
        
        # Add suggested reactions for each result
        for i in range(1, self.queue.length+1):
            emoji = self.NUMBER_TO_EMOJI[i]
            await message.add_reaction(emoji)
            await asyncio.sleep(0.7)
        
        # Wait for reactions.
        content = None
        try:
            reaction, user = await self.bot.wait_for(event='reaction_add', check=self.reaction_add_check, timeout=30.0)
            num = self.EMOJI_TO_NUMBER[reaction.emoji]
            self.queue.dequeue(num-1)
            content = f'Removed song at position **#{num}.**'
            await interaction.send(content)
    
        # Irrelevant reactions will stop the search. Should dedicate work to another function that gracefully handles irrelevant reactions without making the search useless.
        except KeyError as e:
            content = 'Invalid reaction'
            await interaction.send(content)
        except IndexError as e:
            content="You somehow reacted with a number too large or too small. Dumbass."
            await interaction.send(content) # what if the user sends a mistaken reaction. needs to be a more robust check.
    
        except asyncio.TimeoutError:
            content = 'request timed out'
            await interaction.send(content, delete_after=3.0)
            await message.delete(delay=5.0)
        
        except Exception as e:
            print("uknown error occuring")
            content = e
        
        finally:
            print(content)
    
    @nextcord.slash_command(name='skip', description="Skip to the next song", guild_ids=[])
    async def skip(self, interaction: Interaction):
        # Check for connectedness
        vc: nextcord.VoiceClient = interaction.guild.voice_client #type: ignore
        if not vc:
            await interaction.send("Bot not connected to any channel")
            return
        
        # Check queue
        global queue
        if self.queue.isEmpty or self.queue.length==1:
            await interaction.send('Queue is already empty!')
            await vc.disconnect(force=True)
            return
        
        node = self.queue.dequeue()
        if vc.is_playing(): vc.stop()
    
        # Notify channel of song change w/ some markdown hyperlinks and formatting
        await interaction.send(f'1. [{node.title}]({node.url}) - {node.artist} ({node.length})')
        vc.play(node.source, after=self.streamEndsOrError(interaction)) 

    
    
    # TODO - Checks for the type of reaction given to a message (when called). Takes same arguements as the on_reaction_add event.
    def reaction_add_check(self, reaction: nextcord.Reaction, user: Union[nextcord.Member, nextcord.User]) -> bool:
        print("Checking if reaction is organic")
        emoji = reaction.emoji
        return not( user.bot and EMOJI_TO_NUMBER.get(emoji) ) #type: ignore