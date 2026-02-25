-- fp => filepath
-- script intended for sqlite processing

CREATE TABLE IF NOT EXISTS SongData(
    id INTEGER PRIMARY KEY,
    yt_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    duration TEXT NOT NULL,
    artist TEXT NOT NULL DEFAULT 'N/A',
    creator_str TEXT NOT NULL DEFAULT 'N/A',
    uploader TEXT NOT NULL DEFAULT'N/A',
    cover_art_fp TEXT NOT NULL DEFAULT 'default_cover_art.jpg',
    audio_fp TEXT NOT NULL
);