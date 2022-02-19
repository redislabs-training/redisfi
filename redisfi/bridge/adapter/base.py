from flask_socketio import SocketIO
from cleo import Command
from redis import Redis

class BaseAdapter:
    def __init__(self, cli: Command, assets: list, crypto: list, redis_url: str, **kwargs) -> None:
        self.cli = cli
        self.redis = Redis.from_url(redis_url)
        self.socket = SocketIO(message_queue=redis_url)
        self.assets = assets
        self.crypto = crypto

    def live_update(self, obj):
        self.socket.emit('update', obj)

    def run():
        raise NotImplementedError