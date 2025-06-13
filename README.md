# badeni
 - Fully-featured music bot for Discord. 
 - Utilises [nextcord](https://github.com/nextcord/nextcord/) library.
 - Implements modern slash commands.

# Motivations
Due to the perpetually changing nature of 

# Dependencies
1. FFMPEGaudio - for processing audio before streaming to Discord
2. [yt-dlp](https://github.com/yt-dlp/yt-dlp)

# Installation
1.  Clone the project into your  directory. 
2. Install [FFmpeg](https://ffmpeg.org/) for your appropriate OS/deployment environment. (For Windows users) Ensure that the executables is added to the PATH environment variable. Guide listed [here](https://youtu.be/K7znsMo_48I?si=3Rtbex1mGwJmD0FC)
2. Set up  and env file containing you r server id and the bot token.
3. Activate the virtual environment with the relevant command for your operating system.
	e.g  `venv/Scripts/activate` with Powershell on Windows.
4. Create an .env file for your SoundCloud and Discord Bot tokens. 
5. Run the bot by  using  `python3 bot.py`.


Goals
1. - [ ] request audio from Youtube (or other streaming options)
2. - [ ] queueing up songs, playlists, DJ role
2. - [ ] create storage solution for a set amount of time. (read up on how large volumes of data are queried with insane speed. What is Elastisearch?)
3. - [ ] modularise and build testing suite for the bot
4. - [ ] support for sharding