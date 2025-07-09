import nextcord
from nextcord.ext import commands
import dotenv
import logging
import random
import subprocess
# import yt_dlp

# Logging
logger = logging.getLogger('nextcord')
logger.setLevel(logging.ERROR)
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

# Bot & gateway intents setup.
intents = nextcord.Intents.default()
bot = commands.Bot(intents=intents)

#Assign variable for the channel connection.
botVoiceClient: nextcord.VoiceClient = None

#======================== Intitial Commands ================================#
@bot.event
async def on_ready():
    #Load media files from elsewhere
    connections = bot.voice_clients

    for vc in connections:
        await vc.disconnect(forcgit ade=True)
    
    print(f'We have logged in as {bot.user}')

# When bot goes offline and completely disconnects from discord.
@bot.event
async def on_disconnect():
    connections = bot.voice_clients

    for vc in connections:
        await vc.disconnect(force=True)

    print("The bot disconnected fr. Should also disconnect voice connections everywhere.\n")


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


#======================== Connection Commands & Logic ================================#

@bot.slash_command(name="join", description="Join current voice channel", guild_ids=[])
async def join(interaction: nextcord.Interaction):
    await interaction.response.defer(ephemeral=True,with_message=True)

    #identify user voice state
    botVoiceClient: nextcord.VoiceClient | None = interaction.guild.voice_client # type: ignore
    userVoiceState = interaction.user.voice

    if (userVoiceState == None):
        await interaction.followup.send("not in a voice channel")
    elif (botVoiceClient and botVoiceClient.channel == userVoiceState.channel):
        # What if you don't want users to move the bot relentessly
        await interaction.followup.send("bot already connected to this channel") 
    else:
        channel = userVoiceState.channel
        # I think <timeout> controls how long it takes for the bot to disconnect due to inactivity.
        await channel.connect(reconnect=True) 
        await interaction.followup.send("should join now")

@bot.slash_command(name="leave", description="Leave the current voice channel.", guild_ids=[])
async def leave(interaction: nextcord.Interaction):
    vc = interaction.guild.voice_client
    channel = interaction.user.voice.channel
    if (channel.type != None):
        await vc.disconnect(force=True)
        await interaction.send("bot has left")
    else:
        await interaction.send("you are not in a voice channel") 

"""
def sameBotUserVoiceChannel(func):
    async def wrapper(interaction: nextcord.Interaction, *args, **kwargs):
        global botVoiceClient
        
        # gonna really lock in tomorrow
        member = interaction.guild.get_member(interaction.user.id) # pylance errors due to lack of null checks and what not. could be dangerous ma boi. This is where the errors can start to pile up if I'm not careful
        userVC = interaction.user.voice.channel
        if userVC==None:
            await interaction.send("User isn't in a voice channel")
        elif botVoiceClient.is_connected() and botVoiceClient.

    return wrapper
"""

# Called when a stream ends or an error occurs.
# can i pass an interaction? can I edit// override the function to take the interactionm
async def streamEndsOrError(error):
    global botVoiceClient
    print("stream ended or there was an error trying to play the audio")
    await botVoiceClient.disconnect()
    botVoiceClient = None

#======================== Initial Playback Commands ================================#

def get_audio_subprocess(form: str, url: str):
    completed_process = subprocess.run(
        args=['yt-dlp.exe', '-x', '-g', '--audio-format', form, url],
        capture_output=True,
        text=True
    )
    return completed_process

@bot.slash_command(description="tests for YTDL audio fetching", guild_ids=[])
async def test_ytdlp_play(
    interaction: nextcord.Interaction,
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
    
    await interaction.response.defer(ephemeral=True,with_message=True) # Make user wait for response

    # Try get OPUS url.
    audio_url: str | None = None
    source: nextcord.FFmpegOpusAudio | nextcord.FFmpegPCMAudio | None = None 
    try: # Opus URL
        process = get_audio_subprocess('opus', url)
        process.check_returncode()
        audio_url = process.stdout
        source = nextcord.FFmpegOpusAudio(source=audio_url)

    # Could these calls to get_audio_process be done asyncronosly.
    except subprocess.CalledProcessError: # Alternative enconding URLs
        forms = ['best', 'aac', 'alac', 'flac', 'm4a', 'mp3', 'vorbis','wav']
        for form in forms:
            process = get_audio_subprocess(form=form, url=url)

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

            # Could be multiple types of exceptions occuring

    # Could be multiple types of exceptions occuring
    except:
        print('unknown error occured during Opus URL acquirement')
    
    finally:
        if audio_url and source:
            vc.play(source=source, after=streamEndsOrError)
            print(f'source type: {type(source)}')
            await interaction.followup.send("playing audio now")
        else:
            await interaction.followup.send("badeni couldn't process your request") 


# Plays a song at a given link. Runs through entire song. Only works for local files
@bot.slash_command(description="Testing for attempt to play (specific) local audio file successfully", guild_ids=[TESTING_GUILD_ID])
async def test_play(interaction: nextcord.Interaction):
    #identify user and channel.
    global botVoiceClient
    print("Running function")
    
    userChannel = interaction.user.voice.channel
    userVoice = interaction.user.voice
    botChannel = botVoiceClient.channel

    assert(botVoiceClient != None)
    
    if (botChannel.type == None):
        await interaction.send("the bot is not in a channel")
    elif (userVoice == None):
        await interaction.send("the user is not in a channel rn")
    elif (botChannel == userChannel):
        # Create audio source
        fp = r'C:\Users\Abdul\OneDrive\Documents\Discord Bots\stiff\media\tester.mp3'
        fp2 = r'C:\Users\Abdul\OneDrive\Documents\Discord Bots\stiff\media\Skepta x Smooth Soul 2 [K5Ywq18TeVA].webm'
        fp3 = r'C:\Users\Abdul\OneDrive\Documents\Discord Bots\stiff\media\opus_skeppy.opus'

        source = nextcord.FFmpegOpusAudio(fp3)
        botVoiceClient.play(source=source, after=streamEndsOrError)
        await interaction.send("planning to play audio")
    else:
        await interaction.send("wrong channel buddy")
    # Fetch the data to be played.


@bot.slash_command(description="Pauses playback.", guild_ids=[TESTING_GUILD_ID])
async def test_pause(interaction: nextcord.Interaction):
    global botVoiceClient

    botVoiceClient.pause()
    await interaction.send("pausing it now")

@bot.slash_command(description="Pauses badeni", guild_ids=[TESTING_GUILD_ID])
async def test_resume(interaction: nextcord.Interaction):
    global botVoiceClient
    
    botVoiceClient.resume()
    await interaction.send("resuming now")
    

# hello command
@bot.slash_command(description="My first slash command.", guild_ids=[])
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello!")

# Run bot
if token == None:
    print("ERROR: no bot token found")
else:
    bot.run(token)
