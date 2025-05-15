import nextcord
from nextcord.ext import commands
import dotenv
import logging
import random
import discord
import io


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
TESTING_GUILD_ID = int(config['TESTING_GUILD_ID'])  # Make sure this is an int

# Bot & gateway intents setup.
intents = discord.Intents.default()
bot = commands.Bot(intents=intents)

#Assign variable for the channel connection.
botVoiceClient: nextcord.VoiceClient = None

@bot.event
async def on_ready():
    #Load media files from elsewhere
    print(f'We have logged in as {bot.user}')


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


@bot.slash_command(name="join", description="Join current voice channel", guild_ids=[TESTING_GUILD_ID])
async def join(interaction: nextcord.Interaction):
    global botVoiceClient

    #identify user voice state
    userVoiceState = interaction.user.voice
    if (userVoiceState == None):
        await interaction.send("not in a voice channel")
    else:
        channel = interaction.user.voice.channel
        botVoiceClient = await channel.connect(timeout = 2.0)
        assert(botVoiceClient != None)

        await interaction.send("should join now")

@bot.slash_command(name="leave", description="Leave the current voice channel.", guild_ids=[TESTING_GUILD_ID])
async def leave(interaction: nextcord.Interaction):
    channel = interaction.user.voice.channel
    if (channel.type != None):
        await interaction.guild.voice_client.disconnect()
        await interaction.send("bot has left")
    else:
        await interaction.send("you are not in a voice channel")

# Plays a song at a given link. Runs through entire song. Only works for local files
# link: String = nextCord.SlashOption(description="link")

@bot.slash_command(description="Test for playing audio successfully", guild_ids=[TESTING_GUILD_ID])
async def test_play(interaction: nextcord.Interaction):
    #identify user and channel.
    global botVoiceClient
    
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
        buffer: io.BufferedIOBase = None
        fp = r'C:\Users\Abdul\OneDrive\Documents\Discord Bots\stiff\media\tester.mp3'
        with open(fp, 'rb') as file:
            buffer = io.BufferedIOBase(file)
            source = nextcord.FFmpegPCMAudio(source=fp)
            
            # Test audio
            botVoiceClient.play(source=source, after=streamEndsOrError)
            await interaction.send("planning to play audio")
    else:
        await interaction.send("wrong channel buddy")
    # Fetch the data to be played.
    
# Called when a stream ends or an error occurs.
async def streamEndsOrError(error):
    botVoiceClient.disconnect()
    botVoiceClient = None


# hello command
@bot.slash_command(description="My first slash command.", guild_ids=[TESTING_GUILD_ID])
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello!")

# Run bot
bot.run(token)
