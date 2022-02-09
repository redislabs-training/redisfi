from threading import Thread
from queue import Queue

from redis import Redis

class StreamReader(Thread):
    def __init__(self, name: str, queue: Queue, redis_config={}, block=1000) -> None:
        super().__init__()
        self.R = Redis(**redis_config)
        self.name = 'stream:' + name
        self.block = block
        self.running = False
        self.queue = queue

    def run(self):
        if self.running:
            return
        
        self.running = True

        while self.running:
            last_id = '$'
            results = self.R.xread({self.name:last_id}, block=self.block)
            for _, entries in results:
                for entry_id, entry in entries:
                    last_id = entry_id
                    print(f'stream reader got {entry}')
                    self.queue.put(entry, block=False)

    def stop(self):
        self.running = False
        self.join()

    def shutdown(self, *_):
        self.stop()