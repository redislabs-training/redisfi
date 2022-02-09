from redis import Redis

class StreamWriter:
    def __init__(self, name, redis_config={}) -> None:
        self.R = Redis(**redis_config)
        self.name = 'stream:' + name

    def write(self, obj):
        self.R.xadd(self.name, obj)

