from redis import Redis

class StreamWriter:
    def __init__(self, name, redis_config={}) -> None:
        self.R = Redis(**redis_config)
        self.name = 'stream:' + name

    def write(self, obj, name=None):
        if name is None:
            name = self.name
        else:
            name = f'{self.name}:{name}'
            
        self.R.xadd(name, obj)

