from QueueNode import QueueNode
'''
Queue class for the purpose of creating a queue of songs for a user to add to.
For the bot to be active, there should be at least one song in the queue 
i.e. the song currently playing. 
'''
class Queue:

    
    
    def __init__(self, limit = 10) -> None:
        # self.limit = limit
        self.queue: list[QueueNode] = []
        self._limit = limit

    @property
    def length(self):
        return len(self.queue)

    @property
    def limit(self):
        return self._limit
    
    @limit.setter
    def limit(self, limit):
        if limit < len(self.queue):
            raise ValueError("Limit cannot smaller than the queue size.")
        else:
            self._limit = limit

    @property
    def isEmpty(self) -> bool:
        return len(self.queue)==0

    def enqueue(self, node: QueueNode, posi: int = 0) -> IndexError | None :
        if len(self.queue)==10:
            raise IndexError()
        else:
            self.queue.insert(posi, node)
    
    def dequeue(self, index:int = 0) -> QueueNode:
        return self.queue.pop(index)
        
    def get(self, index: int) -> QueueNode:
        return self.queue[index]

    def swap(self, a: int, b: int) -> None:
        temp = self.queue[a]
        self.queue[a] = self.queue[b]
        self.queue[b] = temp

    def clear(self) -> None:
        self.queue.clear()
    
   

    
