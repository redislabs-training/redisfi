from json import dumps
from threading import Thread
from queue import Queue

from redis import Redis

class StreamReader:
    def __init__(self, name: str, redis_config:dict={}, block=1000) -> None:
        self.R = Redis(**redis_config)
        self.name = 'stream:' + name
        self.block = block
        self.last_id = '$'

    def read(self, track_last=True, serialize=False):
        results = self.R.xread({self.name:self.last_id}, block=self.block)
        for _, entries in results:
            for entry_id, entry in entries:
                if track_last:
                    self.last_id = entry_id
                    print(f'stream reader got : {entry}')
                if serialize:
                    entry = dict([(str(k), str(v)) for k,v in entry.items()])
                    entry = dumps(entry)

                yield entry

class StreamReaderThread(StreamReader, Thread):
    def __init__(self, name: str, queue: Queue, redis_config={}, block=1000) -> None:
        super().__init__()
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
                    print(f'stream reader put in queue: {self.queue}')
    def stop(self):
        self.running = False
        self.join()

    def shutdown(self, *_):
        self.stop()