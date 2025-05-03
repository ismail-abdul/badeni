import nextcord
from nextcord.ext import commands
import dotenv
import logging
import random
import discord

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

# Bot setup
# Setup gateway intents
intents = discord.Intents.default()
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    #Load media files from elsewhere
    print(f'We have logged in as {bot.user}')

# hello command
@bot.slash_command(description="My first slash command.", guild_ids=[TESTING_GUILD_ID])
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello!")

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
    #identify user
    channel = interaction.user.voice.channel
    if (channel.type != None):
        await interaction.send("should join now")
        await channel.connect(timeout = 2.0)
    else:
        await interaction.send("not in a voice channel")

@bot.slash_command(name="leave", description="Badeni will leave the current voice channel.", guild_ids=[TESTING_GUILD_ID])
async def leave(interaction: nextcord.Interaction):
    channel = interaction.user.voice.channel
    if (channel.type != None):
        await interaction.guild.voice_client.disconnect()
        await interaction.send("bot has left")
    else:
        await interaction.send("you are not in a voice channel")


# Run bot
bot.run(token)
