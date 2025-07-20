from nextcord import FFmpegPCMAudio, FFmpegOpusAudio
class QueueNode:
    def __init__(self, artist: str, length: int, source: FFmpegPCMAudio | FFmpegOpusAudio) -> None:
        self.artist = artist # artist/channel/uploader's name
        self.length = length # length in seconds
        self.source = source # URL for the extracted audio link
        self.is_opus = isinstance(source, FFmpegOpusAudio) # Encoding format: opus (true) or other (false) e.g. wav, aac, mp4 etc