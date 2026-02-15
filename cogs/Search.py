import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member
from typing import List, Dict, Any, Optional, Union
import yt_dlp
import asyncio

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

    def __init__(self, bot: nextcord.Client, audio_ydl: yt_dlp.YoutubeDL, search_ydl: yt_dlp.YoutubeDL):
        self.bot = bot
        self.audio_ydl = audio_ydl
        self.search_ydl = search_ydl

    
    @nextcord.slash_command(name='search', description="Search for and play a song", guild_ids=[])
    async def search_command(self,
        interaction: Interaction, 
        query: str = nextcord.SlashOption(description="YT search query", required=True), 
        result_count : int = nextcord.SlashOption(description="Num of returned results", default=1, min_value=1, max_value=5)
    ):
    # if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=False, with_message=True)
    
        # print(f'Here\'s the queue length before search_command is executed: {queue.length}')
        # Check for bot being joined already.
    
        '''Allows user to search for videos.'''
        content = ''
        entries = await self.ytsearch(query, result_count)
        if len(entries) == 0:
            await interaction.send("badeni couldn't find any results")
            return
        
        # Collect and format results.se
        for i in range(len(entries)):
            entry = entries[i]
            webpage_url = entry['webpage_url']
            duration_string = entry['duration_string']
            title = entry['title']
            uploader = entry['uploader']
            result = f'{i+1}. {title} - **{uploader} ({duration_string})**\n URL: {webpage_url} \n'
            content += result
        
        # Send message
        await interaction.followup.send(content=content, ephemeral=False)
        message = await interaction.original_message()
        
        # Add suggested reactions for each result
        for i in range(1, len(entries)+1):
            emoji = self.NUMBER_TO_EMOJI[i]
            await message.add_reaction(emoji)
            await asyncio.sleep(0.7)
        
        # Wait for reactions.
        try:
            reaction, user = await bot.wait_for(event='reaction_add', check=self.reaction_add_check, timeout=30.0)
            num = EMOJI_TO_NUMBER[reaction.emoji]
            entry = entries[num-1]
            webpage_url = entry['webpage_url']
            print("Attempting to play")
            await self.play_url_command(interaction=interaction, url=webpage_url, entry=entry) # just play the url.
            
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
    
    
    # Fetches information about a certain LESS IS MORE record in SongData. Then uses filepath to get access to file and stream.
    # Assumes user is already connected
    """
    @nextcord.slash_command(name="localstream", description="Testing data retrieval & streaming pipeline from our Database.", guild_ids=[])
    async def fetchAndStream_command(self, interaction: Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=False, with_message=True)
        global cur
        global conn
    
        # Attempt to fetch data from the DB.
        yt_id="Aizpvina1Fs"
        statement = "SELECT audio_fp From SongData WHERE yt_id = ?;"
        try:
            results = cur.execute(statement, yt_id)
        except sqlite3.ProgrammingError:
            await interaction.send("Failed to retrieve data")
            return
        
        fp = results.fetchone()[0]
        expected_fp = r'songs\Aizpvina1Fs.opus'
        print(f'retrieved: {fp} | expected: {expected_fp}')
    
        if fp != expected_fp:
            await interaction.send("Filepaths failed to match up")
        else:
            source: FFmpegOpusAudio = FFmpegOpusAudio(fp)
            vc: VoiceClient= interaction.guild.voice_client #type: ignore
            vc.play(source)
            await interaction.send("Trying to play file now")
        """

    async def ytsearch(self, 
            query: str,
            result_count: int, 
        ) -> List[Dict[str, Any]]:
    
        def func(query, result_count):
            # NOTE: If application uses multi-threading, ensure you use locks on global variables.
            global search_ydl
            URL = f'ytsearch{result_count}: {query}'
            info: Dict[str, Any] = search_ydl.extract_info(URL, download=False) # type: ignore
            return info.get('entries', [])
    
        # Validate and classify link.
        loop = asyncio.get_running_loop()
        entries = await loop.run_in_executor(
            None, 
            func, query, result_count
        )
        return entries
    
    def reaction_add_check(self, reaction: nextcord.Reaction, user: Union[nextcord.Member, nextcord.User]) -> bool:
        print("Checking if reaction is organic")
        emoji = reaction.emoji
        return not( user.bot and EMOJI_TO_NUMBER.get(emoji) ) #type: ignore
        