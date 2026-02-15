import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member
import dotenv
from typing import List, Dict, Any, Optional, Union
import asyncio

# Load .env config
dotenv.load_dotenv()
config = dotenv.dotenv_values()
token = config['DISCORD_BOT_TOKEN']
test_guild_id = config["TESTING_GUILD_ID"]
assert(token != None)
assert(test_guild_id != None)
TESTING_GUILD_ID = int(test_guild_id)  # Make sure this is an int

'''
ConnectionCog
PlaybackCog
SeekCog
SearchCog
DBCog
'''

class Playback(commands.Cog):
    def __init__(self, bot, cur, audio_ydl):
        self.bot = bot
        self.cur = cur
        self.audio_ydl = audio_ydl
        # other inherited information
        # playback shouldn't need access to the queue. I only want play, pause, seek mb

    
    @nextcord.slash_command(description="Pauses playback.", guild_ids=[TESTING_GUILD_ID])
    async def pause(self, interaction: nextcord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        vc: VoiceClient | None = None
        try:
            vc = interaction.guild.voice_client #type: ignore
            assert (vc != None)
        except Exception as e:
            await interaction.send("badeni experienced an unforseen error")
            print(e)
            return
        
        if vc.is_playing():
            vc.pause()
            await interaction.send("resuming now")
        else:
            await interaction.send("nothing is playing?")

    @nextcord.slash_command(description="Resumes playback", guild_ids=[TESTING_GUILD_ID])
    async def resume(self, interaction: nextcord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        vc : VoiceClient | None = None
        try:
            vc = interaction.guild.voice_client #type: ignore
            assert (vc != None)
        except Exception as e:
            await interaction.send("badeni experienced an unforseen error")
            print(e)
            return
        
        if vc.is_paused:
            vc.resume()
            await interaction.send("resuming it now")
        else:
            await interaction.send("there's nothing to pause.")

    async def play_url_command( self,
        interaction: Interaction, 
        url: str,
        entry: Dict[str, Any],
        ydl_opts: Optional[Dict[str, Any]] = None,
    ):
        """Plays audio from a specific YT video, specified by an URL.
        Should prioriize database first. Then go to YT to search and update DB."""
    
        # Check database for an instance first.
        yt_id = url[-12::]
        global cur
        res = self.cur.execute(
            'SELECT * FROM Tracks WHERE yt_id = ?;', yt_id
        )
        track = res.fetchone()
        if track != None:
            # Needs better design function is getting too long.
            pass
    
        # Manage queue. Take the url, download the file.
        global audio_ydl
        loop = asyncio.get_running_loop()
        info = await loop.run_in_executor(
            None, 
            lambda: self.audio_ydl.extract_info(url, download=True) 
        )
        
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
        
        if not queue.isFull:
            node = QueueNode(artist=artist, length=entry['duration_string'], source=source, url=url, title=entry['title'])
            queue.enqueue(node)
        else:
            await interaction.send("queue is full")
    
        # Respond to user accordingly.  
        try:
            ext = entry['ext']
            print(f'Extension: {ext}')
        except:
            print("Couldn't find extension in <entry> variable")
        finally:
            print(f'command received: {url}')
            await interaction.send("recieved")
    
    
        
