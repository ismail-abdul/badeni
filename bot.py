import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio
import dotenv
import logging
import random
import subprocess
from Queue import Queue
from QueueNode import QueueNode
from typing import List, Dict, Any, Optional
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
def streamEndsOrError(interaction: Interaction, error: Exception | None = None):
    """
    Using a higher order function provides context to func without breaking the defintion for after.
    Once called, this lower func with 'hidden' context is returned. 
    Hence, we have an finalizer function/coroutine with only error. In theory, 
    we could apply args and kwargs to this pattern.
    """
    async def func(error: Exception | None):
        global queue # type: Queue
        await interaction.response.defer(ephemeral=False, with_messasge=True)
        vc: VoiceClient = interaction.guild.voice_client # type: ignore

        # i.e. connection loss, player fails to process audio, server fails etc. Need to handle each case seperately later.
        if error: 
            await vc.disconnect()
            queue.clear()
            await interaction.send("Error whilst playing")
            return 
        
        if queue.isEmpty:
            await vc.disconnect()
            await interaction.send("Stream ended.")
            return
        
        node: QueueNode = queue.dequeue()
        vc.play(source=node.source, after = streamEndsOrError(interaction, error))
        await interaction.send('Playing the next song.') # Improve UX here. Need to make some cool embeds. Mb some templating can be created.
    
    return func

#========================= Queue Management =========================================#

@bot.slash_command(name="queue", description="See the current state of the queue.", guild_ids=[])
async def queue_state(interaction: Interaction):
    pass

@bot.slash_command(name="clear", description="Cleares the queue w/o skipping the current song", guild_ids=[])
async def clear(interaction: Interaction):
    pass

@bot.slash_command(name="remove", description="Remove song from queue", guild_ids=[])
async def remove(interaction: Interaction):
    pass

@bot.slash_command(name="insert", description="Insert song into queue", guild_ids=[])
async def insert(interaction: Interaction, position: int = nextcord.SlashOption(name="positon", description="Position of insertion")):
    pass

@bot.slash_command(name='skip', description="Skip to the next song", guild_ids=[])
async def skip(interaction: Interaction):
    pass


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

@bot.slash_command(description="tests for YTDL audio fetching", guild_ids=[])
async def test_ytdlp_play(
    interaction: Interaction,
    url: str = nextcord.SlashOption(description="YT URL"),
):
    # Check for bot being joined already.
    guild: nextcord.Guild | None = interaction.guild
    if guild == None or guild.id != TESTING_GUILD_ID:
        await interaction.send("incorrect guild//server origin for this command")
        return
    
    vc: nextcord.VoiceClient | None = guild.voice_client # type: ignore
    if vc == None:
        await interaction.send("bot hasn't joined channel")
        return

    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=True,with_message=True) # Make user wait for response


    # Try get OPUS url.
    audio_url: str | None = None
    source: nextcord.FFmpegOpusAudio | nextcord.FFmpegPCMAudio | None = None 
    try: # Opus URL
        process = await get_audio_subprocess('opus', url)
        process.check_returncode()
        audio_url = process.stdout
        source = nextcord.FFmpegOpusAudio(source=audio_url)

    # Could these calls to get_audio_process be done asyncronosly.
    except subprocess.CalledProcessError: # Alternative enconding URLs
        content = "yt_dlp subprocess failed"
        print(content)

        forms = ['aac', 'alac', 'flac', 'm4a', 'mp3', 'vorbis','wav']
        for form in forms:
            process = await get_audio_subprocess(form=form, url=url)

            try: # Check for successful extraction
                process.check_returncode()
                audio_url = process.stdout
                print(f'The url is {audio_url}')
                source = nextcord.FFmpegPCMAudio(source=audio_url)
                break # exit for loop

            except subprocess.CalledProcessError:
                print("yt_dlp command failed.")
                continue
            except nextcord.ClientException:
                print('FFmpegPCMAudio object creation failed')
                continue
            except:
                print('unexpected error occured')
                continue
    
    # Link is likely invalid
    except subprocess.TimeoutExpired: 
        content="Subprocess timed out. Likely due to a faulty link"
        print(content)

    # Opus Source creation failure or poor user input
    except nextcord.ClientException as e: 
        content = "Opus Source creation failed."
        print(content)

    # Could be multiple types of exceptions occuring
    except:
        content = "unknown error occured during audio URL acquirement"
        print(content)
    
    # Play audio, enqueue or handle error.
    finally:
        if audio_url and source:
            global queue

            if queue.isEmpty:
                after = streamEndsOrError(interaction)
                vc.play(source=source, after=after)
                content = "playing audio now"
            else:
                content = "added song to the queue"
            
            print(content)
            node = QueueNode('None', 0, source)
            queue.enqueue(node)
            print(f'source type: {type(source)}')
        else: 
            content = "badeni couldn't process your request"

        await interaction.send(content)

    # TODO - need a means of detecting when song ends, dequueing from player and continuing


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
        info: Dict[str, Any] | None = ydl.extract_info(URL, download=False)
        entries = info['entries']
        return info.get('entries', [])

async def validateVoiceCommand(interaction: Interaction):
    '''Validated interaction for voice based commands'''
    guild: nextcord.Guild | None = interaction.guild
    if guild == None or guild.id != TESTING_GUILD_ID:
        await interaction.send("incorrect guild//server origin for this command")
        return
    
    vc: nextcord.VoiceClient | None = guild.voice_client # type: ignore
    if vc == None:
        await interaction.send("bot hasn't joined channel")
        return

    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=False,with_message=True) # Make user wait for response

@bot.slash_command(description="plays audio from a specific YT URL", guild_ids=[])
async def play_url(
    interaction: Interaction, 
    url: str = nextcord.SlashOption(description="YT URL", required=True)
    ):
    """Plays audio from a specific YT video, specified by an URL.
    Should prioriize database first. Then go to YT to search and update DB."""

    # Check for bot being joined already.
    await validateVoiceCommand(interaction)
    
@bot.slash_command(description="Search for and play a song", guild_ids=[])
async def play(
    interaction: Interaction, 
    query: str = nextcord.SlashOption(description="YT search query", required=True), 
    result_count : int = nextcord.SlashOption(description="Num of returned results", default=1, min_value=1, max_value=5)
    ):

    # Check for bot being joined already.
    await validateVoiceCommand(interaction)

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
    
    print(f'\n type of sent_message: {type(message)}\n')
    
    # Add suggested reactions for each result
    for i in range(1, len(entries)+1):
        emoji = NUMBER_TO_EMOJI[i]
        print(emoji)
        await message.add_reaction(emoji)
        await asyncio.sleep(0.7)
    





# TODO - Checks for the type of reaction given to a message (when called). Takes same arguements as the on_reaction_add event.
# I also don't really like how song selection is at the moment.
# The user shouldn't have to find the reaction manually
# Instead,  reactions should be easily accessible for the number of songs searched for.
# They should be added by the bot and then detected 
def reaction_add_check(reaction, user) -> bool:
    # TODO - handle reactions to search results messages.
    # Organic reaction and bot message. Very low integrity. Improve later
    
    return not( user.bot or (not reaction.message.author.bot) or (not reaction.emoji in EMOJI_TO_NUMBER) )

# 
@bot.slash_command(description="Get results for a youtube search", guild_ids=[])
async def test_yt_search(
    interaction: Interaction,
    search_inp: str = nextcord.SlashOption(required=True, name='search', description="Pretend you're searching YT."),
    result_count: int = nextcord.SlashOption(required=False, description='Choose x results', min_value=1, max_value=10, default=1)
):
    
    await interaction.response.defer(ephemeral=False, with_message=True)
    results: list[Dict[str, str]] | None = None
    try:
        results = get_ytsearch_results(result_count=result_count,search_inp=search_inp,) # really should be called asynchronously if possible
        content = ''
        
        for i in range(len(results)):
            line = f'{i}. '
            result = results[i]
            for field in DEFAULT_PRINT_FIELDS:
                line += f'**{field}**: {result[field]} | '
            line += '\n'
            line.removesuffix(' ')
            content += line
        
        message = await interaction.send(content=content) # Replace with embed later on.
                
        try:
            reaction, user = await bot.wait_for(event='reaction_add', check=reaction_add_check, timeout=30.0)
            number_emoji_map = {
                "1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5,
                "6️⃣": 6, "7️⃣": 7, "8️⃣": 8, "9️⃣": 9, "🔟": 10
            }
            if reaction.emoji in number_emoji_map and 0 < number_emoji_map[reaction.emoji] and number_emoji_map[reaction.emoji] <= result_count:
                num = number_emoji_map[reaction.emoji] - 1
                result = results[num-1] 
                webpage_url = result['webpage_url'] # same fields as JSON data for yt_dlp

                await test_ytdlp_play(interaction=interaction, url=webpage_url) # # just play the url.
            else:
                await interaction.send(content="Invalid arguments") # what if the user sends a mistaken reaction. needs to be a more robust check.



        except asyncio.TimeoutError:
            await interaction.send(content="Your request timed out.")
        
    except subprocess.CalledProcessError:
        await interaction.send("badeni couldn't process the request")


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
