from flask_socketio import SocketIO
from cleo import Command
from redis import Redis
from redisfi.db import index_bar_json, index_asset_json


class BaseAdapter:
    def __init__(self, cli: Command, assets: list, crypto: list, redis_url: str, **kwargs) -> None:
        self.cli = cli
        self.redis = Redis.from_url(redis_url)
        self.indexes = [index_bar_json, index_asset_json]
        self.socket = SocketIO(message_queue=redis_url)
        self.assets = assets
        self.crypto = crypto

        self._init_indexes()

    def _init_indexes(self):
        for index in self.indexes:
            index(self.redis)

    def live_update(self, name, obj):
        self.socket.emit(f'updates.{name}', obj)

    def run():
        raise NotImplementedError
