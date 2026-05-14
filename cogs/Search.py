import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member
from typing import List, Dict, Any, Optional, Union
import yt_dlp
import asyncio
from services.Search import Search as SearchService

"""
Commands and methods related to searching local and web-based
sources of music.

Returning search results, paths, fields from a database. 
"""

class Search(commands.Cog):
    DEFAULT_PRINT_FIELDS =  ('artist','webpage_url','title')
    EMOJI_TO_NUMBER = {
        "1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5,
        "6️⃣": 6, "7️⃣": 7, "8️⃣": 8, "9️⃣": 9, "🔟": 10
    }
    NUMBER_TO_EMOJI = {v:k for k,v in EMOJI_TO_NUMBER.items()}

    AUDIO_OPTS = {
        'format': 'opus/bestaudio',
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
        }],
        'outtmpl': './songs/%(id)s.%(ext)s'
    }


    def __init__(self, bot: commands.Bot, search: SearchService):
        self.bot = bot
        self.search_service = search
    
    def user_results_msg(self, entries):
        content = ''
        for i in range(len(entries)):
            entry = entries[i]
            webpage_url = entry['webpage_url']
            duration_string = entry['duration_string']
            title = entry['title']
            uploader = entry['uploader']
            result = f'{i+1}. {title} - **{uploader} ({duration_string})**\n URL: {webpage_url} \n'
            content += result
        return content
    
    async def pick_result(self, entries, message, interaction: Interaction) -> int:
        """
        Waits for user to pick from the results. 
        Choice discarded if user takes too long to react.
        Returns corresponging entries index number (provided user picks in time).
        """
        content = ''
        # Add suggested reactions for each result
        for i in range(1, len(entries)+1):
            emoji = self.NUMBER_TO_EMOJI[i]
            await asyncio.sleep(0.7)
            await message.add_reaction(emoji)
        
        # Wait for reactions.
        try:
            reaction, user = await self.bot.wait_for(event='reaction_add', check=self.bot.reaction_add_check, timeout=30.0)
            num = self.EMOJI_TO_NUMBER[reaction.emoji]
            entry = entries[num-1]
            webpage_url = entry['webpage_url']
            print(f'Attempting to play: URL:{webpage_url} (num: {num})')
            return num-1
    
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
        
        except AssertionError as e:
            print("Search Service was unsuccessful")
            print(e)
            await interaction.send('badeni was unable to process your request')
        
        except Exception as e:
            print("uknown error occuring")
            print(e)
        
        finally:
            return -1

    # Maybe that song length limit should be user_configurable
    @nextcord.slash_command(name='search', description="Search for and play a song", guild_ids=[])
    async def search_command(
        self,
        interaction: Interaction, 
        query: str = nextcord.SlashOption(description="YT search query", required=True), 
        result_count : int = nextcord.SlashOption(description="Max number of returned results", default=1, min_value=1, max_value=5)
    ):
        await interaction.response.defer()
        raw_results = await self.search_service.ytsearch(query, result_count)
        content = self.user_results_msg(raw_results)
        msg = await interaction.send(content, ephemeral=False)
        choice = await self.pick_result(raw_results, msg, interaction)
        if choice == -1:
            await interaction.send('badeni couldn\'t process your request')
            return
        
        # Start download if necessary
        
        
    
        
       
       
        


