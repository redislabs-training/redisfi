from redis import Redis
from flask_socketio import SocketIO


class StreamWriter:
    def __init__(self, name, redis_url='redis://') -> None:
        self.R = Redis.from_url(redis_url)
        self.name = 'stream:' + name
        self.socket = SocketIO(message_queue=redis_url)

    def write(self, obj, name=None, emit_to_socket=True):
        if name is None:
            name = self.name
        else:
            name = f'{self.name}:{name}'
            
        if emit_to_socket:
            self.socket.emit('update', obj)
            
        self.R.xadd(name, obj)


