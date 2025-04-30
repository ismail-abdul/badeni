import nextcord
from nextcord.ext import commands
import dotenv
import nextcord
import logging

logger = logging.getLogger('nextcord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


dotenv.load_dotenv()

config = dotenv.dotenv_values()
token = config['DISCORD_BOT_TOKEN']
TESTING_GUILD_ID = config['TESTING_GUILD_ID']


bot = commands.Bot();

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command(description="My first slash command.", guild_ids=[TESTING_GUILD_ID])
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello!")

bot.run(token)