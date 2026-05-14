from yt_dlp import YoutubeDL
import yt_dlp
from typing import Any, Dict, List, Optional
import asyncio

class Search:
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
        'outtmpl': './songs/%(id)s.%(ext)s',
        'concurrent_fragment_downloads': 4
    }


    def __init__(self, audio_opts: Optional[Dict] = None, search_opts: Optional[Dict] = {}):
        # RHS is a fallback value
        self._audio_opts = audio_opts or self.AUDIO_OPTS
        self._search_opts = search_opts or {'match_filter': self.length_filter}

    def length_filter(self, info, *, incomplete, limit = 600):
        """Download only videos longer than 10 minutes (or with unknown duration)"""
        duration = info.get('duration')
        if duration and duration > limit:
            return 'The video is too long'
    

    async def ytsearch(self, query: str, result_count: int):
        """Returns search results from Youtube in Python dictionary-like"""
        def func(query: str, result_count: int):
            URL = f'ytsearch{result_count}: {query}'
            with yt_dlp.YoutubeDL(self._search_opts) as ydl: # type: ignore
                info = ydl.extract_info(URL, download = False)
                return info.get('entries', [])

        # Validate and classify link.
        loop = asyncio.get_running_loop()
        entries = await loop.run_in_executor(
            None, 
            func, query, result_count
        )
        return entries
    

    async def dl_yt_audio_by_Id(self, id: str) -> bool: 
        """
        Download the audio from a given Youtube video. 
        id - specifies the unique YoutubeID for the video.
        Return True if a download is made successfully.
        """
        URL = rf'https://www.youtube.com/watch?v={id}'
        loop = asyncio.get_running_loop()
        with yt_dlp.YoutubeDL(self._audio_opts) as ydl: #type: ignore
            retcode = await loop.run_in_executor(
                None, 
                ydl.download, [URL]
            )
            return retcode == 0
    
    async def dl_yt_audio_by_url(self, url: str) -> bool: 
        """
        Download the audio from a given Youtube video. 
        Return True if a download is made successfully.
        """
        loop = asyncio.get_running_loop()
        with yt_dlp.YoutubeDL(self._audio_opts) as ydl: #type: ignore
            retcode = await loop.run_in_executor(
                None, 
                ydl.download, [url]
            )
            return retcode == 0
