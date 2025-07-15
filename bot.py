import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio
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

# Assign variable for queue.
queue: list[FFmpegOpusAudio | FFmpegPCMAudio] = []


#======================== Intitial Commands ================================#
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
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
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
    elif before.channel == None: # Is it a join event.
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
async def join(interaction: Interaction):
    await interaction.response.defer(ephemeral=True,with_message=True)

    #identify user voice state
    botVoiceClient: VoiceClient | None = interaction.guild.voice_client # type: ignore
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

# Need to add null_safety.
@bot.slash_command(name="leave", description="Leave the current voice channel.", guild_ids=[])
async def leave(interaction: Interaction):
    # Also need to clear the queue in this case.
    vc = interaction.guild.voice_client 
    channel = interaction.user.voice.channel
    if (channel.type != None):
        await vc.disconnect(force=True)
        await interaction.send("bot has left")
    else:
        await interaction.send("you are not in a voice channel") 


# Called when a stream ends or an error occurs.
# can i pass an interaction? can I edit// override the function to take the interactionn
# Supply an interaction to the finaliser funciton. I.e when the stream ends or an error occurs.
async def streamEndsOrError2(interaction: Interaction, error: Exception | None = None):
    
    # task/coroutine can be created but not awaited.
    # return func when the higher order function is executed
    # the func will have the context of the HO. 
    async def func(error: Exception | None):
        global queue
        await interaction.response.defer(ephemeral=False, with_message=True)
        vc: VoiceClient = interaction.guild.voice_client # type: ignore

        if error: # Error during the stream. I.e. intenet connection loss, player fails or smn idk. Need to read more
            # Disconnect voice client and clear the queue
            await vc.disconnect()
            queue.clear()
            await interaction.send("Error whilst playing.")

        else: # Stream ended
            queue.pop()
            if len(queue) == 0:
                await vc.disconnect()
            # Need to decide on correct method for creating the source i.e. is it opus or not
            vc.play(source=queue[0], after = await streamEndsOrError2(interaction, error))
            await interaction.send("Stream ended.")

    return func


#========================= Queue Management =========================================#


#========================= Initial Playback Commands ================================#

def get_audio_subprocess(form: str, url: str):
    completed_process = subprocess.run(
        args=['yt-dlp.exe', '-x', '-g', '--audio-format', form, url],
        capture_output=True,
        text=True
    )
    return completed_process

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
    
    # Play audio, enqueue or handle error.
    finally:
        if audio_url and source:
            after = streamEndsOrError2(interaction)
            vc.play(source=source, after=after)
            print(f'source type: {type(source)}')
            await interaction.followup.send("playing audio now")
        else:
            await interaction.followup.send("badeni couldn't process your request") 


@bot.slash_command(description="Pauses playback.", guild_ids=[TESTING_GUILD_ID])
async def pause(interaction: nextcord.Interaction):
    global botVoiceClient

    botVoiceClient.pause()
    await interaction.send("pausing it now")

@bot.slash_command(description="Resumes playback", guild_ids=[TESTING_GUILD_ID])
async def resume(interaction: nextcord.Interaction):
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
