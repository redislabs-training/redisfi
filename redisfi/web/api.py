from json import dumps

from flask import Blueprint, current_app, request, Response

from redisfi import db as DB

api = Blueprint('api', __name__)

@api.route('/account/<int:account>/transactions')
def account_history(account):
    redis = current_app.config['REDIS']
    start, end = request.args.get('start', 0), request.args.get('end', 'inf')
    symbol = request.args.get('symbol')

    if not (start or start == 0) or not end: # 0 is valid, but also false, so if false make sure not zero
        return 'invalid start/end value', 400

    results = DB.get_transactions(redis, account=account, start=start, end=end, symbol=symbol)
    return dumps(results)


@api.route('/asset/<string:symbol>/history')
def asset_history(symbol:str):
    redis = current_app.config['REDIS']
    start, end = request.args.get('start', 0), request.args.get('end', 'inf')

    if not (start or start == 0) or not end: # 0 is valid, but also false, so if false make sure not zero
        return 'invalid start/end value', 400

    results = DB.get_asset_history(redis, symbol, start, end)
    return dumps(results)

@api.route('/asset/<string:symbol>/prices')
def asset_latest(symbol:str):
    redis = current_app.config['REDIS']
    latest = DB.get_asset_prices(redis, symbol)
    
    if latest:
        return dumps(latest)
    else:
        return Response(status=404)

@api.route('/asset/<string:symbol>/trades')
def asset_trades(symbol:str):
    redis = current_app.config['REDIS']
    start, end = request.args.get('start', 0), request.args.get('end', 'inf')
    
    if not (start or start == 0) or not end: # 0 is valid, but also false, so if false make sure not zero
        return 'invalid start/end value', 400

    results = DB.get_trades(redis, symbol, start, end)
    return dumps(results)
    