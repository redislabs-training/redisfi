from json import dumps

from flask import Blueprint, current_app, request, Response

from redisfi import db as DB

api = Blueprint('api', __name__)

@api.route('/account/<int:account>/<string:kind>/transactions')
def account_history(account, kind):
    redis = current_app.config['REDIS']
    start, end = request.args.get('start', 0), request.args.get('end', 'inf')
    results = DB.get_transactions(redis, account, kind, start, end)
    return dumps(results)


@api.route('/asset/<string:symbol>/history')
def asset_history(symbol:str):
    redis = current_app.config['REDIS']
    start, end = request.args.get('start', 0), request.args.get('end', 'inf')
    results = DB.get_asset_history(redis, symbol, start, end)
    return dumps(results)

@api.route('/asset/<string:symbol>/prices')
def asset_latest(symbol:str):
    redis = current_app.config['REDIS']
    symbol = symbol.upper()
    latest = DB.get_asset_prices(redis, symbol)
    
    if latest:
        return dumps(latest)
    else:
        return Response(status=404)