from redis import Redis
from redis.exceptions import ResponseError
from redis.commands.json.path import Path
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import TextField, NumericField, TagField

_key_asset = lambda symbol: f'asset:{symbol}'
_key_bars = lambda symbol, timestamp: f'bars:{symbol}:{int(timestamp)}'

def get_asset(redis: Redis, symbol: str):
    return redis.json().get(_key_asset(symbol))

def index_asset_json(redis: Redis):
    idx = redis.ft(_key_asset('idx'))
    try:
        idx.info()
        return idx
    except ResponseError:
        pass

    idx.create_index((
        TagField('$.symbol', as_name='symbol'),
        TextField('$.name', as_name='name'),
        TextField('$.description', as_name='description'),
        TextField('$.website', as_name='website'),
        TextField('$.sector', as_name='sector'),
        TextField('$.industry', as_name='industry')
    ), definition=IndexDefinition(prefix=[_key_asset('')], index_type=IndexType.JSON))

    return idx

def index_bar_json(redis:Redis):
    idx = redis.ft(_key_bars('idx', ''))
    try:
        idx.info()
        return idx
    except ResponseError:
        pass

    idx.create_index((
        TagField('$.symbol', as_name='symbol'),
        NumericField('$.timestamp', as_name='timestamp'),
        NumericField('$.open', as_name='open'),
        NumericField('$.high', as_name='high'),
        NumericField('$.low', as_name='low'),
        NumericField('$.close', as_name='close'),
        NumericField('$.volume', as_name='volume')
    ), definition=IndexDefinition(prefix=[_key_bars('','')], index_type=IndexType.JSON))

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

