from gevent import monkey 
monkey.patch_all()

from os import environ
from subprocess import Popen
from datetime import datetime, timedelta
from pprint import pp
from uuid import uuid4
from time import perf_counter

from flask_socketio import SocketIO
from flask import Flask, redirect, render_template, Response, request
from redis import Redis

from redisfi import db as DB
from redisfi.web.api import api
from redisfi.web.research import research
from redisfi.web.research.api import research_api 

ACCOUNT = 710
WORDS_ALLOWED_IN_ASSET_DESCRIPTION = 75
REDIS_URL = environ.get('REDIS_URL', 'redis://localhost:6379')

app = Flask(__name__)
socketio = SocketIO(app, message_queue=REDIS_URL, async_mode='gevent', cors_allowed_origins="*")

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(research, url_prefix='/research')
app.register_blueprint(research_api, url_prefix='/research/api')

app.config['ACCOUNT'] = ACCOUNT
app.config['SECRET_KEY'] = 'supersecret!'
app.config['REDIS'] = Redis.from_url(REDIS_URL)
app.config['VSS_URL'] = environ.get('VSS_URL', 'http://localhost:7777')

DAYS_IN_YEAR = 365.26
_now = lambda: datetime.utcnow()
now = lambda: int(_now().timestamp())
one_day_ago = lambda: int((_now() - timedelta(days=1)).timestamp())
one_week_ago = lambda: int((_now() - timedelta(days=7)).timestamp())
thirty_days_ago = lambda: int((_now() - timedelta(days=30)).timestamp())
ninty_days_ago = lambda: int((_now() - timedelta(days=90)).timestamp())
a_year_ago = lambda: int((_now() - timedelta(days=DAYS_IN_YEAR)).timestamp())
time_kwargs = lambda: {'now':now(), 'day':one_day_ago(), 'week':one_week_ago(), 'thirty':thirty_days_ago(), 'ninty':ninty_days_ago(), 'year':a_year_ago()}

_log_guid = lambda: str(uuid4())

def _truncate_description(description):
    desc_list = description.split(' ')

    if len(desc_list) > WORDS_ALLOWED_IN_ASSET_DESCRIPTION:
        return ' '.join(desc_list[0:WORDS_ALLOWED_IN_ASSET_DESCRIPTION]) + '...'
    else:
        return ' '.join(desc_list)

def _sum_portfolio_balance(portfolio: dict):
    balance = portfolio['retire']['value']

    assets = {}
    assets.update(portfolio['stocks'])
    assets.update(portfolio['crypto'])
    assets.update(portfolio['etfs'])

    for asset, shares_owned in assets.items():
        prices = portfolio['price'][asset]
        price = prices['live'] or prices['mock'] or prices['historic']
        balance += price * shares_owned

    return balance

@app.route('/')
def landing():
    return render_template('landing.jinja')

@app.route('/overview')
def portfolio():
    redis = app.config['REDIS']
    log_guid = _log_guid()
    
    start = perf_counter()
    portfolio_data = DB.get_portfolio(redis, ACCOUNT, log_guid=log_guid)
    end = perf_counter()
    total_db_time = (end - start)*1000
    
    portfolio_data['balance'] = _sum_portfolio_balance(portfolio_data)
    return render_template('overview.jinja', account=ACCOUNT, portfolio=portfolio_data, log_guid=log_guid, total_db_time=total_db_time, **time_kwargs())

@app.route('/search')
def search():
    redis = app.config['REDIS']
    query = request.args.get('query')
    log_guid = _log_guid()

    if query:
        start = perf_counter()
        results = DB.search_assets(redis, query, log_guid=log_guid)
        
        for result in results:
            if result['price']['live'] is None and result['price']['mock'] is None:
                result['price']['historic'] = DB.get_asset_price_historic(redis, result['symbol'], log_guid=log_guid)
            else:
                result['price']['historic'] = ''
        end = perf_counter()
        
        return render_template('results.jinja', results=results, log_guid=log_guid, total_db_time=(end-start)*1000)

    else:
        return redirect('/')

@app.route('/asset/<string:symbol>')
def asset(symbol:str):
    redis = app.config['REDIS']
    log_guid = _log_guid()
    
    start = perf_counter()
    asset_data = DB.get_asset(redis, symbol, log_guid=log_guid)
    end = perf_counter()
    total_db_time = (end - start)*1000

    asset_data['description'] = _truncate_description(asset_data['description'])

    if asset_data:
        return render_template('asset.jinja', asset=asset_data, log_guid=log_guid, total_db_time=total_db_time, **time_kwargs())
    else:
        return Response(status=404)


@app.route('/fund/<string:name>')
def fund(name:str):
    redis : Redis = app.config['REDIS']
    log_guid = _log_guid()

    start = perf_counter()
    fund_data = DB.get_fund(redis, name, log_guid=log_guid)

    if fund_data:
        fund_data['assets']  = DB.get_fund_assets_metadata_and_latest(redis, ACCOUNT, fund_data['assets'].keys(), log_guid=log_guid)
        fund_data['balance'] = DB.get_fund_value_aggregate(redis, ACCOUNT, name, page=(0, 1), log_guid=log_guid)[0][1]
        end = perf_counter()
        total_db_time = (end - start)*1000

        return render_template('fund.jinja', fund=fund_data, account=ACCOUNT, log_guid=log_guid, total_db_time=total_db_time, **time_kwargs())

    else:
        return Response(status=404)


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
