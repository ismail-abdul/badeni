"""
Entry point of application.
Instantiate the custom bot (sub)class.
"run" the bot => connecting to discord api, going online etc
"""

from bot import Badeni
from services.queue import Queue
from services.Search import Search
import dotenv
import logging

# Logging
logger = logging.getLogger('nextcord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Load .env config
dotenv.load_dotenv()
config = dotenv.dotenv_values()
token: str = config['DISCORD_BOT_TOKEN'] # type: ignore
test_guild_id = config["TESTING_GUILD_ID"]
assert(token != None)
assert(test_guild_id != None)

badeni = Badeni(queue=Queue(limit=10), search_service=Search())
badeni.run(token)