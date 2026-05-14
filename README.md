# badeni

A self-hosted Discord music bot built with [nextcord](https://github.com/nextcord/nextcord/). Streams audio from YouTube directly into voice channels using modern slash commands.

## Features

| Command | Description |
|---|---|
| `/join` | Join your current voice channel |
| `/leave` | Leave the current voice channel |
| `/play` | Find and play a track by query |
| `/search` | Search YouTube and pick from up to 5 results |
| `/pause` | Pause the current track |
| `/resume` | Resume a paused track |
| `/queue` | Display the current playback queue |
| `/enqueue` | Add a song to the queue |
| `/dequeue` | Remove a song from the queue |
| `/skip` | Skip to the next track |
| `/clear` | Clear the queue without stopping the current track |

## Prerequisites

- **Python 3.10+**
- **FFmpeg** — install for your OS and ensure the executable is on your `PATH`
  - Windows guide: [https://youtu.be/K7znsMo_48I](https://youtu.be/K7znsMo_48I?si=3Rtbex1mGwJmD0FC)

## Installation

1. Clone the repository:
   ```
   git clone <repo-url>
   cd stiff
   ```

2. Create and activate a virtual environment:
   ```bash
   # Create
   python -m venv venv

   # Activate (Windows PowerShell)
   venv\Scripts\activate

   # Activate (macOS / Linux)
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
DISCORD_BOT_TOKEN=your_bot_token_here
TESTING_GUILD_ID=your_guild_id_here
```

- `DISCORD_BOT_TOKEN` — obtained from the [Discord Developer Portal](https://discord.com/developers/applications)
- `TESTING_GUILD_ID` — the ID of the Discord server (guild) the bot will register slash commands in

## Running

```
python bot.py
```

The bot will log in, register slash commands to the configured guild, and be ready to accept commands.

## Planned Features

- [ ] Automated test suite
- [ ] Sharding support for multi-server deployments
- [ ] Persistent song history via SQLite
- [ ] Embedded now-playing cards with track metadata
- [ ] SoundCloud support
