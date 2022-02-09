from os import environ
from subprocess import PIPE, Popen

from flask import Flask, stream_with_context

app = Flask(__name__)

@app.route('/')
def index():
    return 'i started!'

@app.route('/updates')
def updates():
    pass

def run(debug):
    if debug:
        env = environ.copy()
        env.update({"FLASK_APP":__file__, 'FLASK_DEBUG':'1'})
        with Popen(['poetry', 'run', 'flask', 'run'], env=env) as _app:
            _app.communicate()
    else:
        with Popen(['poetry', 'run', 'gunicorn', 'redisfi.web.app:app']) as _app:
            _app.communicate()