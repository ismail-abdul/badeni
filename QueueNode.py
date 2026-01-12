from nextcord import FFmpegPCMAudio, FFmpegOpusAudio
class QueueNode:
    def __init__(self, artist: str | None, length: int, source: FFmpegPCMAudio | FFmpegOpusAudio, title: str | None = "N/A", duration = 0, url: str = 'N/A' ) -> None:
        if artist is None or artist.strip() == "": 
            artist = "N/A"
        if title is None or artist.strip() == "":
            title = "N/A"
        self.artist: str = artist # artist/channel/uploader's name
        self.length: int = length # length in seconds
        self.source: FFmpegPCMAudio | FFmpegOpusAudio = source # URL for the extracted audio link
        self.title: str = title
        self.is_opus: bool = isinstance(source, FFmpegOpusAudio) # Encoding format: opus (true) or other (false) e.g. wav, aac, mp4 etc
        self.url: str = url