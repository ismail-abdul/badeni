import nextcord
import nextcord.ext.commands as commands
from nextcord import Member, VoiceState, VoiceClient, Interaction, FFmpegOpusAudio, FFmpegPCMAudio, User, Member
import dotenv
import logging
import random
import subprocess
from Queue import Queue
from QueueNode import QueueNode
from typing import List, Dict, Any, Optional, Union
import asyncio
import yt_dlp


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
            EMOJI_TO_NUMBER = {
                "1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5,
                "6️⃣": 6, "7️⃣": 7, "8️⃣": 8, "9️⃣": 9, "🔟": 10
            }
            emoji = reaction.emoji
            if 0 < EMOJI_TO_NUMBER[emoji] and EMOJI_TO_NUMBER[emoji] <= result_count:
                num = EMOJI_TO_NUMBER[emoji] - 1
                result = results[num-1] 
                webpage_url = result['webpage_url'] # same fields as JSON data for yt_dlp

                await test_ytdlp_play(interaction=interaction, url=webpage_url) # # just play the url.
            else:
                await interaction.send(content="Invalid arguments") # what if the user sends a mistaken reaction. needs to be a more robust check.



        except asyncio.TimeoutError:
            await interaction.send(content="Your request timed out.")
        
    except subprocess.CalledProcessError:
        await interaction.send("badeni couldn't process the request")

