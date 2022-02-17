from typing import Text
from redis import Redis
from redis.exceptions import ResponseError
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import TextField

_key_bars = lambda symbol: f'bars:{symbol}'
_key_stock = lambda symbol: f'stock:{symbol}'

def index_stock_json(redis: Redis):
    idx = redis.ft(_key_stock('idx'))
    try:
        idx.info()
        return idx
    except ResponseError:
        pass

    idx.create_index((
        TextField('$.name', as_name='name'),
        TextField('$.description', as_name='description'),
        TextField('$.website', as_name='website'),
        TextField('$.sector', as_name='sector'),
        TextField('$.industry', as_name='industry')
    ), definition=IndexDefinition(prefix=[_key_stock('')], index_type=IndexType.JSON))

    return idx

def set_bar(redis: Redis, symbol: str, timestamp: int, open: float,
             high: float, low: float, close: float, volume: int):
   
    redis.zadd(_key_bars(symbol),{f'{open}|{high}|{low}|{close}|{volume}':timestamp})

def set_stock_json(redis: Redis, symbol: str, name: str, description: str, website: str, 
                   sector: str, industry: str):
    
    obj = {'name':name, 
           'description':description, 
           'website':website, 
           'sector':sector, 
           'industry':industry}

    redis.json().set(_key_stock(symbol), '$', obj)

