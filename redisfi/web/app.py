
from os import environ
from subprocess import Popen
from typing import Iterator

from flask_socketio import SocketIO
from flask import Flask, render_template
# from flask_sse import Message

# from redisfi.db.stream.reader import StreamReader


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, message_queue='redis://', async_mode='gevent')

@app.route('/')
def index():
    print('test')
    return render_template('base.html')

@socketio.on('message')
def handle_message(data):
    print(f'received message: {data}')

# @app.route('/updates')
# def updates():
    
#     @stream_with_context
#     def sse_wrapper(stream: Iterator):
#         for item in stream:
#             item = dict([(k.decode('ascii'), v.decode('ascii')) for k,v in item.items()])
#             yield str(Message(item))

#     stream_reader = StreamReader('bridge:alpaca:trades:CBSE:BTCUSD')
#     return app.response_class(sse_wrapper(stream_reader.read()), mimetype='text/event-stream')

def run(debug=False):
    if debug:
        with Popen(['poetry', 'run', 'python3', 'redisfi/web/app.py']) as _app:
            _app.communicate()
    else:
        with Popen(['poetry', 'run', 'gunicorn', '-w', '4', '--worker-class', 'gevent', 'redisfi.web.app:app']) as _app:
            _app.communicate()

if __name__ == '__main__':
    socketio.run(app, debug=True)