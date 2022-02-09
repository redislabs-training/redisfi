from redisfi.db.stream.writer import StreamWriter

class BaseAdapter(StreamWriter):
    def __init__(self, name, **kwargs) -> None:
        name = 'bridge:' + name
        super().__init__(name, **kwargs)

    def run():
        raise NotImplementedError