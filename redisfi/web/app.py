from os import environ
from subprocess import Popen
from queue import Queue
from signal import signal, SIGINT, SIGTERM

from flask import Flask, stream_with_context

from redisfi.db.stream.reader import StreamReader

app = Flask(__name__)
alpaca_queue = Queue()

@app.route('/')
def index():
    return 'i started!'

@app.route('/updates')
def updates():
    stream_reader = StreamReader('bridge:alpaca')
    return app.response_class(stream_with_context(stream_reader.read(serialize=True)), mimetype='text/event-stream')




def run(debug):
    # alpaca_stream_reader = StreamReader('bridge:alpaca', alpaca_queue)
    
    # signal(SIGINT, alpaca_stream_reader.shutdown)
    # signal(SIGTERM, alpaca_stream_reader.shutdown)

    # alpaca_stream_reader.start()

    if debug:
        env = environ.copy()
        env.update({"FLASK_APP":__file__, 'FLASK_DEBUG':'1'})
        with Popen(['poetry', 'run', 'flask', 'run'], env=env) as _app:
            _app.communicate()
    else:
        with Popen(['poetry', 'run', 'gunicorn', 'redisfi.web.app:app']) as _app:
            _app.communicate()