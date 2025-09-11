from Queue import Queue
from QueueNode import QueueNode
import subprocess
from typing import Dict
from nextcord import FFmpegPCMAudio, FFmpegOpusAudio

# Really want this to run asynchronously or in parallel.
def get_yt_search_result_links(search: str, num: int = 5):
    # yt-search
    completed_process = subprocess.run(
        args=['yt-dlp.exe', '--print', 'title', '--print', 'artist', '--print', 'webpage_url', f'ytsearch{num}: {search} '],
        capture_output=True,
        text=True
    )
    return completed_process



def test_queue():
    q = Queue(limit=10)

    for i in range(10):
        node = QueueNode(artist="J Cole",length=i, audio_url=str(i))
        q.enqueue(node=node)

    try:
        print(f'Current Q length: {len(q.queue)}')
        node = QueueNode(artist="J Cole",length=55, audio_url=str(5))
        q.enqueue(node=node)
    except IndexError:
        print("The queue is full. And you tryna add stuff?? How greedy")

    try:
        while True:
            print(f'Current Q length: {len(q.queue)}')
            q.dequeue()
    except:
        print("ITAMIIII.")
        print(f'Current Q length: {len(q.queue)}')

def test_queue_2():
    opus_1 = FFmpegOpusAudio(source='media/opus_skeppy.opus')
    other_1 = FFmpegPCMAudio(source='media/Skepta_x_Smooth_Soul_2_[K5Ywq18TeVA].webm')
    queue = Queue()
    print(queue.isEmpty)
    queue.enqueue(node=QueueNode('Skepta', 3, opus_1))
    print(queue.isEmpty)
    queue.enqueue(node=QueueNode('Skepta', 3, other_1))
    print(queue.isEmpty)
    
'''
Generates a yt-dlp subprocess that searches Youtube. Then returns the data specifed by the --print arguments.
@param search_inp is searched for in Youtube
@param result_count number results extracted from the YT search.
@param args the field data to be extracted. Arguments be found in the OUTPUT TEMPLATE part of the github repo's README.

@return A dict of the form {arg: value}. e.g. {'artist': 'PlaqueBoyMax, Skepta, 5STAR'}

@raise subprocess.CalledProcessError if an error occurs within the yt-dlp subprocess
I wish args and kwargs were ideal here. I want an excuse to use them in a function. 
Acc I could, but then we taking up double memory unecessarily (asymptotically of course).
'''
def get_ytsearch_results(search_inp: str,
                         result_count: int = 5, 
                         args: tuple[str, ...] = ('artist','webpage_url','title')) ->  list[Dict[str, str]]:

    # _args = [*args,] -> Comma tells interpreter 'we r defining a tuple literal'. field = *args, is usually too ambiguous, but here with the square braces, it's unnecessary. 
    _args = list(args)

    # insert --print before each requested field
    limit = len(_args)
    i = 0
    while i < limit:
        _args.insert(i, '--print')
        i+=2 # skips to next argument
        limit = len(_args)
        
    print(f'Current args: {*_args, }')
    
    # Supply the yt-dlp executable and URL argument (which triggers a youtube search)
    _args.append(f'ytsearch{result_count}: {search_inp}')
    _args.insert(0, 'yt-dlp.exe')

    
    completed_process = subprocess.run(
        args=_args,
        capture_output=True,
        text=True
    )

    completed_process.check_returncode()
    raw_out: list[str] = (completed_process.stdout).split('\n')
    raw_out = [line for line in raw_out if line.strip()] # Remove blank lines
    # print(f'Line split list: \n {(*raw_out,)}')

    for i in raw_out:
        print(i)

    # Split output into a list of result dictionaries.
    result_list = []
    for i in range(0, len(raw_out), len(args)): # i --> 
        # print(f'i: {i}')
        result = {} # ith result

        for j in range(0, len(args), 1):
            # print(f'j: {j}')
            key = args[j] # jth key
            value = raw_out[i+j]
            result[key] = value

        result_list.append(result) # store the result

    
    return result_list
'''
Is it possible to dictionary the data available.
Yes ofc. But that requires some manual manipulation of the text.
Split by new line. Then supply names and extract values
'''


def test_ytsearch_1():
    result_count = 3
    less_is_more=get_yt_search_result_links('skepta less is more', result_count)
    try:
        less_is_more.check_returncode()
        output = less_is_more.stdout
        results = less_is_more.stdout.split(sep='\n')
        field_count = 3
        

        for i in range(len(results)//field_count):
            output = f'''
({i+1}) - 
Title: {results[i*field_count]}   Artist: {results[i*field_count+1]} \n
URL: {results[i*field_count+2]}\n 
            '''
            print(output)

    except subprocess.CalledProcessError:
        print('smn went wrong during the PS command process')
        print(less_is_more.stderr)

    except Exception as e:
        print(f'unforseen error met \n {e}')
    
    finally:
        print('finished w subprocess')

def test_ytsearch_2():
    args: tuple[str,...] = ('artist', 'webpage_url', 'title')

    less_is_more=get_ytsearch_results(search_inp='skepta less is more', 
                                      args=args,
                                      result_count=3)
    for posi in range(len(less_is_more)):
        print(f'Current Position: {posi}')
        result = less_is_more[posi]
        print(result)

def main():
    # test_ytsearch_2()
    test_queue_2()

if __name__ == '__main__':
    main()
    




