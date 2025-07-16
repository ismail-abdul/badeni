class QueueNode:
    def __init__(self, artist: str, length: int, audio_url: str, is_opus: bool = False) -> None:
        self.artist = artist # artist/channel/uploader's name
        self.length = length # length in seconds
        self.audio_url = audio_url # URL for the extracted audio link
        self.is_opus = is_opus # Encoding format: opus (true) or other (false) e.g. wav, aac, mp4 etc