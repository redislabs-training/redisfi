from flask_socketio import SocketIO
from cleo import Command
from redis import Redis

from redisfi import db as DB
from redisfi.db import index_bar, index_asset, index_transaction, index_asset_portfolio_value, index_component, index_trade

class BaseAdapter:
    def __init__(self, cli: Command, assets: list, crypto: list, redis_url: str, **kwargs) -> None:
        self.cli = cli
        self.redis = Redis.from_url(redis_url)
        self.indexes = [index_bar, index_asset, index_transaction, index_asset_portfolio_value, index_component, index_trade]
        self.socket = SocketIO(message_queue=redis_url)
        self.assets = assets
        self.crypto = crypto

        self._init_indexes()

    def _init_indexes(self):
        for index in self.indexes:
            index(self.redis)

    def live_trade_update(self, symbol, obj):
        self.socket.emit(f'updates.{symbol}', obj)
        DB.set_trade(self.redis, symbol, obj['price'], obj['timestamp'], 'live')

    def mock_trade_update(self, symbol, obj):
        self.socket.emit(f'updates.{symbol}', obj)
        DB.set_trade(self.redis, symbol, obj['price'], obj['timestamp'], 'mock')

    def run():
        raise NotImplementedError
