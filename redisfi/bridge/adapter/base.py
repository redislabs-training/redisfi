from flask_socketio import SocketIO
from cleo import Command

class BaseAdapter:
    def __init__(self, name: str, cli: Command, us_stocks: list, crypto: list, 
                 redis_url='redis://', **kwargs) -> None:
        name = 'bridge:' + name
        self.cli = cli
        self.socket = SocketIO(message_queue=redis_url)
        self.us_stocks = us_stocks
        self.crypto = crypto

    def update(self, obj):
        self.socket.emit('update', obj)

    def run():
        raise NotImplementedError