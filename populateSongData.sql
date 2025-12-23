-- You should explore 
-- 1using json data to populate the databse
/* Explore using JSON data and sqlite json functions
to populate database. Could make process more reliable.
Might also be faster than directly constructing the records I want
*/

-- don't specify an id, it will automatically be set
-- need check constraint on the length of yt_id, formatting for the creator str, and basic regex for cover_art_fp and audio_fp
-- the channel name can change, realistically, we should be storing the channel_id
-- store file extensions seperate from filenames
-- then you're able to know what type of data is typically being updated
BEGIN;

INSERT INTO SongData(yt_id, title, duration, artist, creator_str, uploader, cover_art_fp, audio_fp) 
VALUES('Aizpvina1Fs', 'Skepta & PlaqueBoyMax - LESS IS MORE (Official Audio)', '00:02:44', 'Skepta', 'Skepta, PlaqueBoyMax', 'plaqueboymax', './cover_art/{id}.png', './media/{id}.{ext}' );

SELECT * FROM SongData WHERE true;

ROLLBACK;