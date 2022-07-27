from json import dumps

from flask import Blueprint, current_app, request, Response

from redisfi import db as DB

api = Blueprint('api', __name__)

@api.route('/account/<int:account>/transactions')
def account_history(account):
    redis = current_app.config['REDIS']
    start, end = request.args.get('start', 0), request.args.get('end', 'inf')
    symbol = request.args.get('symbol')
    log_guid = request.args.get('log_guid')

    if not (start or start == 0) or not end: # 0 is valid, but also false, so if false make sure not zero
        return 'invalid start/end value', 400

    results = DB.get_transactions(redis, account=account, start=start, end=end, symbol=symbol, log_guid=log_guid)
    return dumps(results)

@api.route('/account/<int:account>/value/<string:symbol>')
def account_portfolio_value(account, symbol):
    redis = current_app.config['REDIS']
    start, end = request.args.get('start', 0), request.args.get('end', 'inf')
    log_guid = request.args.get('log_guid')

    if not (start or start == 0) or not end: # 0 is valid, but also false, so if false make sure not zero
        return 'invalid start/end value', 400
    
    results = DB.get_asset_portfolio_value(redis, account, symbol, start, end, log_guid=log_guid)
    return dumps(results)


@api.route('/asset/<string:symbol>/history')
def asset_history(symbol:str):
    redis = current_app.config['REDIS']
    start, end = request.args.get('start', 0), request.args.get('end', 'inf')
    log_guid = request.args.get('log_guid')

    if not (start or start == 0) or not end: # 0 is valid, but also false, so if false make sure not zero
        return 'invalid start/end value', 400

    results = DB.get_asset_history(redis, symbol, start, end, log_guid=log_guid)
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
    log_guid = request.args.get('log_guid')
    
    if not (start or start == 0) or not end: # 0 is valid, but also false, so if false make sure not zero
        return 'invalid start/end value', 400

    results = DB.get_trades(redis, symbol, start, end, log_guid=log_guid)
    return dumps(results)
    
@api.route('/component/<int:account>/<string:component>/value')
def fund_value(account, component):
    redis = current_app.config['REDIS']
    start, end, = request.args.get('start', 0), request.args.get('end', 'inf')
    log_guid = request.args.get('log_guid')
    
    if not (start or start == 0) or not end: # 0 is valid, but also false, so if false make sure not zero
        return 'invalid start/end value', 400

    results = DB.get_component_value_aggregate(redis, account, component, start, end, log_guid=log_guid)
    return dumps(results)

@api.route('/commands/<string:guid>')
def commands(guid: str):
    redis = current_app.config['REDIS']
    start_at = request.args.get('start_at')

    commands, last_id = DB.get_commands(redis, guid, start_at)
    return dumps({'commands':commands, 'last_id':last_id})


    