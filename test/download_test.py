from services.Search import Search
import os
import time
import asyncio
from pathlib import Path

def construct_path(path: str, id: str, ext: str):
    # 'outtmpl': './songs/%(id)s.%(ext)s'
    ptr = 0
    while path[ptr] != '%':
        ptr += 1
    path = './' + path[0:ptr] + id + '.' + ext
    return Path(path)

def timer(func, *args):
    async def wrapper(*args, **kwargs):
        a = time.time()
        await func(*args, **kwargs)
        b = time.time()
        hours = int((b-a) // (60**2))
        minutes = int((b-a) // 60)
        seconds = int((b-a) % (60))
        print(f'time taken: {hours}:{minutes}:{seconds}')
    return wrapper
    
    

@timer
async def test(id='Uc7XoL25AIA'):
    """Run this test from the 'stiff' directory."""
    service: Search = Search()
    print(service._audio_opts['outtmpl'])
    path = construct_path(service._audio_opts['outtmpl'], id, 'opus')
    if os.path.exists(path): 
        print("File already exists")
        os.remove(path)
    await service.dl_yt_audio_by_Id(id)
    assert os.path.exists(path), "Specified file not found at the generated path"
    print("File found")

# _service: Search = Search()
if __name__ == '__main__':
    print(os.path.abspath(os.path.curdir))
    asyncio.run(main=test())
