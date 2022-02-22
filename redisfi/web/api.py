from json import dumps

from flask import Blueprint, current_app, request

from redisfi import db as DB

api = Blueprint('api', __name__)

@api.route('/asset/<string:symbol>/history')
def asset_history(symbol:str):
    redis = current_app.config['REDIS']
    symbol = symbol.upper()
    start, end = request.args.get('start', 0), request.args.get('end', 'inf')
    results = DB.get_asset_history(redis, symbol, start, end)
    return dumps(results)
