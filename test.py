from Queue import Queue
from QueueNode import QueueNode

if __name__ == '__main__':
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



