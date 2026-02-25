# from nextcord import FFmpegPCMAudio, FFmpegOpusAudio
class QueueNode:
    def __init__(self, artist: str | None, length: int, source = None, title: str | None = "N/A", duration = 0, is_opus: bool = False,  url: str = 'N/A', **kwargs) -> None:
        if artist is None or artist.strip() == "": 
            artist = "N/A"
        if title is None or artist.strip() == "":
            title = "N/A"
        self.artist: str = artist # artist/channel/uploader's name
        self.length: int = length # length in seconds
        self.source = source
        self.title: str = title
        self.is_opus: bool = is_opus # Encoding format: opus (true) or other (false) e.g. wav, aac, mp4 etc
        self.url: str = url