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

# Logging
logger = logging.getLogger('nextcord')
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

# Bot & gateway intents setup.
intents = nextcord.Intents.default()
bot = commands.Bot(intents=intents)

# Assign variable for queue.
queue: Queue = Queue(limit=20)

''' NOTE:
interaction.send is really cool because it uses method overloading 
    to change the specfic funciton called based on interaction response state.
Read more at https://docs.nextcord.dev/en/stable/api.html#nextcord.Interaction.send .
'''

#======================== (Webhook) Event Listeners ================================#
@bot.event
async def on_ready():
    #Load media files from elsewhere
    connections = bot.voice_clients

    for vc in connections:
        await vc.disconnect(force=True)
    
    print(f'We have logged in as {bot.user}')

# When bot goes offline and completely disconnects from discord.
@bot.event
async def on_disconnect():
    connections = bot.voice_clients

    for vc in connections:
        await vc.disconnect(force=True)

    print("The bot disconnected fr. Should also disconnect voice connections everywhere.\n")

# Called when a Member changes their VoiceState. 
# In our case, we are using it to check for bot inactivity.
@bot.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState, active: bool = False):
    if not active:
        return
    
    print(f'\nThere was a state change.')
    
    if bot.user == None:
        return
    if member.id != bot.user.id: # check that member is our bot
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

# ======================== Basic Commands ======================================== #

# roll command 
@bot.slash_command(description="Roll a random number between two integers.", guild_ids=[TESTING_GUILD_ID])
async def roll(
    interaction: nextcord.Interaction,
    minimum: int = nextcord.SlashOption(description="Minimum number"),
    maximum: int = nextcord.SlashOption(description="Maximum number")
):
    if minimum > maximum:
        await interaction.send("⚠️ Minimum cannot be greater than maximum!", ephemeral=True)
        return

    result = random.randint(minimum, maximum)
    await interaction.send(f"🎲 You rolled a **{result}** (from {minimum} to {maximum})")

@bot.slash_command(description="Just like the Linux command, echo whatever you type", guild_ids=[])
async def echo(interaction: Interaction, q: str = nextcord.SlashOption(name="q", required=True)):
    await interaction.send(q + ":one:")
#======================== Connection Commands & Logic ================================#

@bot.slash_command(name="join", description="Join current voice channel", guild_ids=[])
async def join(interaction: Interaction):
    await interaction.response.defer(ephemeral=True,with_message=True)

    #identify user voice state
    botVoiceClient: VoiceClient | None = interaction.guild.voice_client # type: ignore
    userVoiceState = interaction.user.voice

    # print(f"Active voice clients: {bot.voice_clients}")
    for vc in bot.voice_clients:
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
@bot.slash_command(name="leave", description="Leave the current voice channel.", guild_ids=[])
async def leave(interaction: Interaction):    
    try:
        # Also need to clear the queue in this case.
        vc = interaction.guild.voice_client # vc will always be used for a VoiceCLeint object. Not a voice channel.
        await vc.disconnect(force=True)
        global queue
        queue.clear()
        await interaction.send("bot has left")
    except:
        if not interaction.guild:
            await interaction.send("command not sent from a guild")
        elif not interaction.guild.voice_client:
            await interaction.send("bot not connected to any voice channels")
        elif not interaction.user:
            await interaction.send("command not sent by a user")
        elif not interaction.user.voice:
            await interaction.send("you are not in a voice channel")
    finally:
        return



# Called when a stream ends or an error occurs.
# can i pass an interaction? can I edit// override the function to take the interactionn
# Supply an interaction to the finaliser funciton. I.e when the stream ends or an error occurs.
# Read https://docs.nextcord.dev/en/stable/faq.html#how-do-i-pass-a-coroutine-to-the-player-s-after-function for info on how to properly do this.
def streamEndsOrError(interaction: Interaction):
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
            await vc.disconnect()
            queue.clear()
            await interaction.send("Error whilst playing")
            print(error)
            return 
        
        if queue.isEmpty:
            await vc.disconnect()
            await interaction.send("Stream ended.")
            return
        
        node: QueueNode = queue.dequeue()
        vc.play(source=node.source, after = streamEndsOrError(interaction))
        await interaction.send('Playing the next song.') # Improve UX here. Need to make some cool embeds. Mb some templating can be created.
    
    return func

#========================= Queue Management =========================================#

@bot.slash_command(name="queue", description="See the current state of the queue.", guild_ids=[])
async def queue_state(interaction: Interaction):
    
    # Validate interaction
    retcode = await validateInteraction(interaction)
    if retcode != 0: return

    # An embed with cool images and alll that would fit perfectly here.

    if queue.isEmpty:
        await interaction.send("queue is empty.")
    
    content='Current Queue: \n'
    for i in range(queue.length):
        node: QueueNode= queue.get(i)
        artist = node.artist
        title = node.title
        length = node.length
        url = node.url
        line = f'{i}. [{title}]({url}) - {artist} ({length})\n'
        content += line
    
    await interaction.send(content)






@bot.slash_command(name="clear", description="Cleares the queue w/o skipping the current song", guild_ids=[])
async def clear(interaction: Interaction):
    queue.clear()
    await interaction.send("Queue has been cleared")

@bot.slash_command(name="remove", description="Remove song from queue", guild_ids=[])
async def remove(interaction: Interaction, choice: int = nextcord.SlashOption(name='choice')):

    # Send message with current queue state
    await queue_state(interaction)
    message = await interaction.original_message()
    
    # Add suggested reactions for each result
    for i in range(1, queue.length+1):
        emoji = NUMBER_TO_EMOJI[i]
        await message.add_reaction(emoji)
        await asyncio.sleep(0.7)
    
    # Wait for reactions.
    content = None
    try:
        reaction, user = await bot.wait_for(event='reaction_add', check=reaction_add_check, timeout=30.0)
        num = EMOJI_TO_NUMBER[reaction.emoji]
        queue.dequeue(num-1)
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

    

@bot.slash_command(name="insert", description="Insert song into queue", guild_ids=[])
async def insert(interaction: Interaction, position: int = nextcord.SlashOption(name="positon", description="Position of insertion")):
    pass

@bot.slash_command(name='skip', description="Skip to the next song", guild_ids=[])
async def skip(interaction: Interaction):
    # Check for connectedness
    retcode = await validateInteraction(interaction)
    vc: nextcord.VoiceClient = interaction.guild.voice_client #type: ignore
    if retcode != 0:
        await interaction.send("Interaction is invalid (to a degree).")
        return
    elif not vc:
        await interaction.send("Bot not connected to any channel")
        return
    
    # Check queue
    global queue
    if queue.isEmpty:
        await interaction.send('Queue is already empty!')
        await vc.disconnect(force=True)
        return
    
    node = queue.dequeue()
    vc.stop()

    # Notify channel of song change w/ some markdown hyperlinks and formatting
    await interaction.send(f'1. [{node.title}]({node.url}) - {node.artist} ({node.length})')
    vc.play(node.source, after=streamEndsOrError(interaction)) 






#========================= Initial Playback Commands ================================#

# TODO - make async safe.
# form - audio-format
async def get_audio_subprocess(form: str, url: str):
    completed_process = subprocess.run(
        args=['yt-dlp.exe', '-x', '-g', '--audio-format', form, url],
        capture_output=True,
        text=True,
        timeout=30
    )
    return completed_process


'''
Generates a yt-dlp subprocess that searches Youtube. Then returns the data specifed by the --print arguments.
@param search_inp is searched for in Youtube
@param result_count number results extracted from the YT search.
@param args the field data to be extracted. Arguments be found in the OUTPUT TEMPLATE part of the github repo's README.

@return A dict of the form {arg: value}. e.g. {'artist': 'PlaqueBoyMax, Skepta, 5STAR'}

@raise subprocess.CalledProcessError if an error occurs within the yt-dlp subprocess
I wish args and kwargs were ideal here. I want an excuse to use them in a function. 
Acc I could, but then we taking up double memory unecessarily (asymptotically of course).

TODO - make this asynchronous if possible. i.e. multiple subprocessess
'''

'''
    Validates interaction for VoiceClient-dependant commands.
    
    Returns a non-zero retcode for invalid interactions.
'''
async def validateInteraction(interaction: Interaction):
    guild: nextcord.Guild | None = interaction.guild
    if guild == None or guild.id != TESTING_GUILD_ID:
        await interaction.send("incorrect guild//server origin for this command")
        return -1
    
    vc: nextcord.VoiceClient | None = guild.voice_client # type: ignore
    if vc == None:
        await interaction.send("bot hasn't joined channel")
        return -1

    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=False,with_message=True) # Make user wait for response
        return 0

async def ytsearch(
        query: str,
        result_count: int, 
        ydl_opts : Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
    
    """Returns the info about the top N results from Youtube. Read the YoutubeDL class for info about the returned dictionaries. """
    
    if ydl_opts is None: 
        ydl_opts = {}

    # Validate and classify link.
    URL = f'ytsearch{result_count}: {query}'
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info: Dict[str, Any] = ydl.extract_info(URL, download=False) #type: ignore
        return info.get('entries', [])


async def play_url_command(
    interaction: Interaction, 
    url: str,
    entry: Dict[str, Any],
    ydl_opts: Optional[Dict[str, Any]] = None,
    ):
    """Plays audio from a specific YT video, specified by an URL.
    Should prioriize database first. Then go to YT to search and update DB."""


    # outttmp1 - Rule for filename output
    # paths - Rule for path for download
    if ydl_opts == None:
        ydl_opts = {
            'format': 'opus/bestaudio',

            'postprocessors': [{  # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
            }],
            
            'outtmpl': './songs/%(id)s.%(ext)s',
        }
    

    # Manage queue. Take the url, download the file.
    with yt_dlp.YoutubeDL(ydl_opts) as ydl: # type: ignore
        info = ydl.extract_info(url, download=True)
        
        # Handle errors.
        '''if retcode != 0:
            print("Download failed")
            await interaction.send('download failed.')
            return'''
        
        # Check queue state. Play song or just enqueue.
        fields = ['creators', 'artist', 'uploader']
        default = 'N/A'
        artist = ''
        for field in fields:
            artist: str = entry.get(field, default)
            if artist != default:
                break
        

        id: str = entry['id']
        ext = info.get('ext')
        path = f'songs/{id}.opus' # hard-coded until I can reliably get the extension
        print(f'source filepath: {path}')
        print(f'post-processed filepath: {info.get('filepath')}')
        source = FFmpegOpusAudio(path)

        
        global queue
        vc: VoiceClient = interaction.guild.voice_client #type: ignore
        if queue.isEmpty:
            # Maybe the interaction is too old?
            print("Playing song now")
            vc.play(source, after=streamEndsOrError(interaction))
        else:
            print(f'Apparently the queue isn\'t empty. {queue.length}')
        
        node = QueueNode(artist=artist, length=entry['duration_string'], source=source, url=url, title=entry['title'])
        queue.enqueue(node)

    # Respond to user accordingly.  
    try:
        ext = entry['ext']
        print(f'Extension: {ext}')
    except:
        print("Couldn't find extension in <entry> variable")
    finally:
        print(f'command received: {url}')
        await interaction.send("recieved")


@bot.slash_command(name='search', description="Search for and play a song", guild_ids=[])
async def search_command(
    interaction: Interaction, 
    query: str = nextcord.SlashOption(description="YT search query", required=True), 
    result_count : int = nextcord.SlashOption(description="Num of returned results", default=1, min_value=1, max_value=5)
    ):

    print(f'Here\'s the queue length before search_command is executed: {queue.length}')
    # Check for bot being joined already.
    returncode =  await validateInteraction(interaction)
    if returncode != 0: return

    '''Allows user to search for videos.'''
    content = ''
    entries = await ytsearch(query, result_count)
    if len(entries) == 0:
        await interaction.send("badeni couldn't find any results")
        return
    
    # Collect and format results.
    for i in range(len(entries)):
        entry = entries[i]
        webpage_url = entry['webpage_url']
        duration_string = entry['duration_string']
        title = entry['title']
        uploader = entry['uploader']
        result = f'{i+1}. {title} - **{uploader} ({duration_string})**\n URL: {webpage_url} \n'
        content += result
    
    # Send message
    await interaction.send(content=content, ephemeral=False)
    message = await interaction.original_message()
    
    # Add suggested reactions for each result
    for i in range(1, len(entries)+1):
        emoji = NUMBER_TO_EMOJI[i]
        await message.add_reaction(emoji)
        await asyncio.sleep(0.7)
    
    # Wait for reactions.
    try:
        reaction, user = await bot.wait_for(event='reaction_add', check=reaction_add_check, timeout=30.0)
        num = EMOJI_TO_NUMBER[reaction.emoji]
        entry = entries[num-1]
        webpage_url = entry['webpage_url']
        print("Attempting to play")
        await play_url_command(interaction=interaction, url=webpage_url, entry=entry) # just play the url.
        print("Smn else should be happening rn/")

    # Irrelevant reactions will stop the search. Should dedicate work to another function that gracefully handles irrelevant reactions without making the search useless.
    except KeyError as e:
        content = 'Invalid reaction'
        print(content)
        await interaction.send(content)
    except IndexError as e:
        print(content)
        content="You somehow reacted with a number too large or too small. Dumbass."
        await interaction.send(content) # what if the user sends a mistaken reaction. needs to be a more robust check.

    except asyncio.TimeoutError:
        content = 'request timed out'
        print(content)
        await interaction.send(content, delete_after=3.0)
        await message.delete(delay=5.0)
    
    except Exception as e:
        print("uknown error occuring")
        print(e)






    # If unresponded to, delete the message.

    # If responded to correctlt, update queue and player.
    

# TODO - Checks for the type of reaction given to a message (when called). Takes same arguements as the on_reaction_add event.
def reaction_add_check(reaction: nextcord.Reaction, user: Union[nextcord.Member, nextcord.User]) -> bool:
    print("Checking if reaction is organic")
    emoji = reaction.emoji
    return not( user.bot and EMOJI_TO_NUMBER.get(emoji) ) #type: ignore
    

@bot.slash_command(description="Pauses playback.", guild_ids=[TESTING_GUILD_ID])
async def pause(interaction: nextcord.Interaction):
    vc = None
    try:
        vc = interaction.guild.voice_client
        vc.pause()
        await interaction.send("pausing it now")
    except:
        if not interaction.guild:
            await interaction.send("command not sent from a guild")
        elif not vc:
            await interaction.send("bot has no voice client for this guild")
        else:
            await interaction.send("badeni experienced an unforseen error")

@bot.slash_command(description="Resumes playback", guild_ids=[TESTING_GUILD_ID])
async def resume(interaction: nextcord.Interaction):
    vc = None
    try:
        vc = interaction.guild.voice_client
        vc.resume()
        await interaction.send("resuming it now")
    except:
        if not interaction.guild:
            await interaction.send("command not sent from a guild")
        elif not vc:
            await interaction.send("bot has no voice client for this guild")
        else:
            await interaction.send("badeni experienced an unforseen error")
    

# hello command
@bot.slash_command(description="My first slash command.", guild_ids=[])
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello!")

# Run bot
if token == None:
    print("ERROR: no bot token found")
else:
    bot.run(token)
