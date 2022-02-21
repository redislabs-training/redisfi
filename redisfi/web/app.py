from os import environ
from subprocess import Popen

from gevent import monkey 
monkey.patch_all()

from flask_socketio import SocketIO
from flask import Flask, render_template
from redis import Redis

from redisfi import db as DB 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret!'
socketio = SocketIO(app, message_queue=environ.get('REDIS_URL'), async_mode='gevent')

@app.route('/asset/<string:symbol>')
def asset(symbol:str):
    redis = app.config['REDIS']
    asset_data = DB.get_asset(redis, symbol.upper())
    print(asset_data)
    return render_template('asset.html', asset=asset_data)

@socketio.on('message')
def handle_message(data):
    print(f'received message: {data}')

def run(debug=False, redis_url='redis://'):
    # This is ultimately a hack around the way the flask debug server works
    # and a way of baking the overall gunicorn run command into the CLI.
    #
    # Take config from CLI (cleo) and plug it into env vars, so the flask
    # app itself is pulling config from env, but that's being driven from 
    # the CLI and handed off here
    env = environ.copy()
    env['REDIS_URL'] = redis_url

    if debug:
        with Popen(['poetry', 'run', 'python3', 'redisfi/web/app.py'], env=env) as _app:
            _app.communicate()
    else:
        with Popen(['poetry', 'run', 'gunicorn', '-w', '4', '--worker-class', 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker', '-b', '0.0.0.0:8000', 'redisfi.web.app:app'], env=env) as _app:
            _app.communicate()

if __name__ == '__main__':
    app.config['REDIS'] = Redis.from_url(environ.get('REDIS_URL', 'redis://localhost:6379'))
    socketio.run(app, debug=True)
