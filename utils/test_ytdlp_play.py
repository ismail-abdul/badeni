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


@bot.slash_command(description="tests for YTDL audio fetching", guild_ids=[])
async def test_ytdlp_play(
    interaction: Interaction,
    url: str = nextcord.SlashOption(description="YT URL"),
):
    # Check for bot being joined already.
    returncode =  await validateInteraction(interaction)
    if returncode != 0: return


    # Try get OPUS url.
    audio_url: str | None = None
    source: nextcord.FFmpegOpusAudio | nextcord.FFmpegPCMAudio | None = None 
    try: # Opus URL
        process = await get_audio_subprocess('opus', url)
        process.check_returncode()
        audio_url = process.stdout
        source = nextcord.FFmpegOpusAudio(source=audio_url)

    # Could these calls to get_audio_process be done asyncronosly.
    except subprocess.CalledProcessError: # Alternative enconding URLs
        content = "yt_dlp subprocess failed"
        print(content)

        forms = ['aac', 'alac', 'flac', 'm4a', 'mp3', 'vorbis','wav']
        for form in forms:
            process = await get_audio_subprocess(form=form, url=url)

            try: # Check for successful extraction
                process.check_returncode()
                audio_url = process.stdout
                print(f'The url is {audio_url}')
                source = nextcord.FFmpegPCMAudio(source=audio_url)
                break # exit for loop

            except subprocess.CalledProcessError:
                print("yt_dlp command failed.")
                continue
            except nextcord.ClientException:
                print('FFmpegPCMAudio object creation failed')
                continue
            except:
                print('unexpected error occured')
                continue
    
    # Link is likely invalid
    except subprocess.TimeoutExpired: 
        content="Subprocess timed out. Likely due to a faulty link"
        print(content)

    # Opus Source creation failure or poor user input
    except nextcord.ClientException as e: 
        content = "Opus Source creation failed."
        print(content)

    # Could be multiple types of exceptions occuring
    except:
        content = "unknown error occured during audio URL acquirement"
        print(content)
    
    # Play audio, enqueue or handle error.
    finally:
        if audio_url and source:
            global queue

            if queue.isEmpty:
                after = streamEndsOrError(interaction)
                vc.play(source=source, after=after)
                content = "playing audio now"
            else:
                content = "added song to the queue"
            
            print(content)
            node = QueueNode('None', 0, source)
            queue.enqueue(node)
            print(f'source type: {type(source)}')
        else: 
            content = "badeni couldn't process your request"

        await interaction.send(content)

    # TODO - need a means of detecting when song ends, dequueing from player and continuing

