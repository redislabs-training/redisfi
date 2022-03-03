from gevent import monkey 
monkey.patch_all()

from os import environ
from subprocess import Popen
from datetime import datetime, timedelta
from pprint import pp

from flask_socketio import SocketIO
from flask import Flask, redirect, render_template, Response, request
from redis import Redis

from redisfi import db as DB
from redisfi.web.api import api 

ACCOUNT = 710

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
app.config['SECRET_KEY'] = 'supersecret!'
app.config['REDIS'] = Redis.from_url(environ.get('REDIS_URL', 'redis://localhost:6379'))
app.config['ACCOUNT'] = ACCOUNT

socketio = SocketIO(app, message_queue=environ.get('REDIS_URL'), async_mode='gevent', cors_allowed_origins="*")

DAYS_IN_YEAR = 365.26
_now = lambda: datetime.utcnow()
now = lambda: int(_now().timestamp())
one_day_ago = lambda: int((_now() - timedelta(days=1)).timestamp())
thirty_days_ago = lambda: int((_now() - timedelta(days=30)).timestamp())
ninty_days_ago = lambda: int((_now() - timedelta(days=90)).timestamp())
a_year_ago = lambda: int((_now() - timedelta(days=DAYS_IN_YEAR)).timestamp())
time_kwargs = lambda: {'now':now(), 'day':one_day_ago(), 'thirty':thirty_days_ago(), 'ninty':ninty_days_ago(), 'year':a_year_ago()}

@app.route('/')
def portfolio():
    return redirect('/fund/retire2050')

@app.route('/search')
def search():
    redis = app.config['REDIS']
    query = request.args.get('query')

    if query:
        results = DB.search_assets(redis, query)
        
        for result in results:
            if result['price']['live'] is None and result['price']['mock'] is None:
                result['price']['historic'] = DB.get_asset_price_historic(redis, result['symbol'])
            else:
                result['price']['historic'] = ''
        
        
        return render_template('results.jinja', results=results)

    else:
        return redirect('/')

@app.route('/asset/<string:symbol>')
def asset(symbol:str):
    redis = app.config['REDIS']
    asset_data = DB.get_asset(redis, symbol)

    if asset_data:
        return render_template('asset.jinja', asset=asset_data, **time_kwargs())
    else:
        return Response(status=404)



@app.route('/fund/<string:name>')
def fund(name:str):
    redis : Redis = app.config['REDIS']
    fund_data = DB.get_fund(redis, name)

    if fund_data:
        fund_data['assets']  = DB.get_assets_metadata_and_latest(redis, ACCOUNT, fund_data['assets'].keys())

        pp(fund_data)

        return render_template('fund.jinja', fund=fund_data, account=ACCOUNT, **time_kwargs())

    else:
        return Response(status=404)

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
        with Popen(['poetry', 'run', 'gunicorn', '--worker-class', 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker', '-b', '0.0.0.0:8000', 'redisfi.web.app:app'], env=env) as _app:
            _app.communicate()

if __name__ == '__main__':
    socketio.run(app, debug=True)
