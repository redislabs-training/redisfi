from email import generator
from os import environ
from subprocess import Popen

from flask import Flask, stream_with_context
from flask_sse import Message

from redisfi.db.stream.reader import StreamReader

app = Flask(__name__)

@app.route('/')
def index():
    return 'i started!'

@app.route('/updates')
def updates():
    
    @stream_with_context
    def sse_wrapper(stream: generator):
        for item in stream:
            item = dict([(k.decode('ascii'), v.decode('ascii')) for k,v in item.items()])
            yield str(Message(item))

    stream_reader = StreamReader('bridge:alpaca')
    return app.response_class(sse_wrapper(stream_reader.read()), mimetype='text/event-stream')

def run(debug=False):
    if debug:
        env = environ.copy()
        env.update({"FLASK_APP":__file__, 'FLASK_DEBUG':'1'})
        with Popen(['poetry', 'run', 'flask', 'run'], env=env) as _app:
            _app.communicate()
    else:
        with Popen(['poetry', 'run', 'gunicorn', 'redisfi.web.app:app']) as _app:
            _app.communicate()