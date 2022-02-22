from json import loads

from redis import Redis
from redis.exceptions import ResponseError
from redis.commands.json.path import Path
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import TextField, NumericField

PAGE_SIZE = 1000000
_key_asset = lambda symbol: f'asset:{symbol}'
_key_bars = lambda symbol, timestamp: f'bars:{symbol}:{int(timestamp) if timestamp else ""}'

def get_asset(redis: Redis, symbol: str):
    return redis.json().get(_key_asset(symbol))

def get_asset_history(redis: Redis, symbol: str, start=0, end='inf'):
    idx = index_bar_json(redis)
    query = Query(f'@symbol:{symbol} @timestamp:[{start},{end}]').sort_by('timestamp', asc=False).paging(0, PAGE_SIZE)
    return _deserialize_results(idx.search(query))

def get_asset_latest(redis: Redis, symbol: str):
    idx = index_bar_json(redis)
    query = Query(f'@symbol:{symbol}').sort_by('timestamp', asc=False).paging(0, 1)
    return _deserialize_results(idx.search(query))

def index_asset_json(redis: Redis):
    idx = redis.ft(_key_asset('idx'))
    try:
        idx.info()
        return idx
    except ResponseError:
        pass

    idx.create_index((
        TextField('$.symbol', as_name='symbol'),
        TextField('$.name', as_name='name'),
        TextField('$.description', as_name='description'),
        TextField('$.website', as_name='website'),
        TextField('$.sector', as_name='sector'),
        TextField('$.industry', as_name='industry')
    ), definition=IndexDefinition(prefix=[_key_asset('')], index_type=IndexType.JSON))

    return idx

def index_bar_json(redis:Redis):
    idx = redis.ft(_key_bars('idx', '')[0:-1])
    try:
        idx.info()
        return idx
    except ResponseError:
        pass

    idx.create_index((
        TextField('$.symbol', as_name='symbol'),
        NumericField('$.timestamp', as_name='timestamp'),
        NumericField('$.open', as_name='open'),
        NumericField('$.high', as_name='high'),
        NumericField('$.low', as_name='low'),
        NumericField('$.close', as_name='close'),
        NumericField('$.volume', as_name='volume')
    ), definition=IndexDefinition(prefix=[_key_bars('','')[0:-1]], index_type=IndexType.JSON))

    return idx

def set_bar_json(redis: Redis, symbol: str, timestamp: int, open: float,
             high: float, low: float, close: float, volume: int):
    
    obj = {'symbol':symbol,
           'timestamp':int(timestamp),
           'open':open,
           'high':high,
           'low':low,
           'close':close,
           'volume':volume}
    key = _key_bars(symbol, timestamp)

    redis.json().set(key, Path.rootPath(), obj)
   

def set_stock_json(redis: Redis, symbol: str, name: str, description: str, website: str, 
                   sector: str, industry: str):
    
    obj = {'symbol':symbol,
           'name':name, 
           'description':description, 
           'website':website, 
           'sector':sector, 
           'industry':industry}

    redis.json().set(_key_asset(symbol), Path.rootPath(), obj)


def _deserialize_results(results) -> list:
    '''turn a list of json at results.docs into a list of dicts'''
    return [loads(result.json) for result in results.docs]