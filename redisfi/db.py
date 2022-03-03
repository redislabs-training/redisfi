from enum import Enum
from json import loads

from redis import Redis
from redis.exceptions import ResponseError
from redis.commands.json.path import Path
from redis.commands.search.commands import SEARCH_CMD, SearchCommands
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import TextField, NumericField

LARGE_PAGE_SIZE = 1000000


_average_bar     = lambda bar: (bar['high'] + bar['low'])/2
_key_asset       = lambda symbol: f'asset:{symbol.upper()}'
_key_bars        = lambda symbol, timestamp: f'bars:{symbol.upper()}:{int(timestamp) if timestamp else ""}'
_key_fund        = lambda id: f'fund:{id}'
_key_trade       = lambda symbol, timestamp: f'trade:{symbol.upper()}:{int(timestamp) if timestamp else ""}'
_key_portfolio_v = lambda account, symbol, timestamp: f'portfolio_value:{account}:{symbol.upper()}:{int(timestamp) if timestamp else ""}'
_key_transaction = lambda account, symbol, timestamp: f'transaction:{account}:{symbol.upper() if symbol else ""}:{int(timestamp) if timestamp else ""}'


def get_asset(redis: Redis, symbol: str):
    return redis.json().get(_key_asset(symbol))


def get_asset_history(redis: Redis, symbol: str, start=0, end='inf', page=(0, LARGE_PAGE_SIZE), asc=False):
    idx = index_bar(redis)
    query = Query(f'@symbol:{symbol} @timestamp:[{start},{end}]').sort_by('timestamp', asc=asc).paging(*page)
    print(_build_search_query(idx, query))
    return _deserialize_results(idx.search(query))


def get_assets_metadata_and_latest(redis: Redis, account: int, symbols: list):
    assets = {}
    for symbol in symbols:
        assets[symbol] = get_asset(redis, symbol)
        assets[symbol]['price']['historic'] = get_asset_price_historic(redis, symbol)
        valid_price = assets[symbol]['price']['live'] or assets[symbol]['price']['mock'] or assets[symbol]['price']['mock']
        assets[symbol]['last_transaction'] = get_transactions(redis, account=account, symbol=symbol, page=(0,1))[0]
        assets[symbol]['growth_percent'] = ((assets[symbol]['last_transaction']['balance'] * valid_price) / assets[symbol]['last_transaction']['total_spent']) * 100

        # print(assets[symbol])
    
    return assets

def get_asset_portfolio_value(redis: Redis, account: int, symbol: str, start=0, end='inf', asc=False, page=(0, LARGE_PAGE_SIZE)):
    idx = index_asset_portfolio_value(redis)
    query = Query(f'@account:{account} @symbol:{symbol.upper()} @timestamp:[{start},{end}]').sort_by('timestamp', asc=asc).paging(*page)
    print(_build_search_query(idx, query))
    return _deserialize_results(idx.search(query))

def get_asset_prices(redis: Redis, symbol: str):
    resp = redis.json().get(_key_asset(symbol), '$.price')

    if resp is not None:
        data = resp[0]

        if type(data) == str:
            resp = loads(resp[0])
        else:
            resp = data
    
    resp['historic'] =  get_asset_price_historic(redis, symbol)
    return resp


def get_asset_price_historic(redis: Redis, symbol: str):
    idx = index_bar(redis)
    query = Query(f'@symbol:{symbol}').sort_by('timestamp', asc=False).paging(0, 1)
    print(_build_search_query(idx, query))
    return _average_bar(_deserialize_results(idx.search(query))[0])


def get_asset_price_live(redis: Redis, symbol: str):
    return redis.json().get(_key_asset(symbol), '$.price.live')


def get_asset_price_mock(redis: Redis, symbol: str):
    return redis.json().get(_key_asset(symbol), '$.price.mock')


def get_fund(redis: Redis, id: str):
    return redis.json().get(_key_fund(id))

def get_trades(redis: Redis, symbol: str, start=0, end='inf', page=(0, LARGE_PAGE_SIZE)):
    idx = index_trade(redis)
    query = Query(f'@symbol:{symbol} @timestamp:[{start},{end}]').sort_by('timestamp', asc=False).paging(*page)
    print(_build_search_query(idx, query))
    return _deserialize_results(idx.search(query))


def get_transactions(redis: Redis, account: int=None, symbol: str=None, start=0, end='inf', page=(0, LARGE_PAGE_SIZE), asc=False):
    idx = index_transaction(redis)

    if symbol is not None:
        symbol_query = f' @symbol:{symbol}'
    else:
        symbol_query = ''

    if account is not None:
        account_query = f' @account:{account}'
    else:
        account_query = ''

    query = Query(f'@timestamp:[{start},{end}]{symbol_query}{account_query}').sort_by('timestamp', asc=asc).paging(*page)
    print(_build_search_query(idx, query))
    return _deserialize_results(idx.search(query))

def index_asset(redis: Redis):
    idx = redis.ft(_key_asset('idx').lower())
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

def index_asset_portfolio_value(redis: Redis):
    idx = redis.ft(_key_portfolio_v('idx', '', '')[0:-2].lower())
    
    try:
        idx.info()
        return idx
    except ResponseError:
        pass

    idx.create_index((
        TextField('$.account', as_name='account'),
        TextField('$.symbol', as_name='symbol'),
        NumericField('$.timestamp', as_name='timestamp', sortable=True)
    ), definition=IndexDefinition(prefix=[_key_portfolio_v('', '', '')[0:-2]], index_type=IndexType.JSON))

    return idx

def index_bar(redis:Redis):
    idx = redis.ft(_key_bars('idx', '')[0:-1].lower())
    try:
        idx.info()
        return idx
    except ResponseError:
        pass

    idx.create_index((
        TextField('$.symbol', as_name='symbol'),
        NumericField('$.timestamp', as_name='timestamp', sortable=True),
        NumericField('$.open', as_name='open'),
        NumericField('$.high', as_name='high'),
        NumericField('$.low', as_name='low'),
        NumericField('$.close', as_name='close'),
        NumericField('$.volume', as_name='volume')
    ), definition=IndexDefinition(prefix=[_key_bars('','')[0:-1]], index_type=IndexType.JSON))

    return idx

def index_trade(redis:Redis):
    idx = redis.ft(_key_trade('idx', '')[0:-1].lower())
    try:
        idx.info()
        return idx
    except ResponseError:
        pass

    idx.create_index((
        TextField('$.symbol', as_name='symbol'),
        NumericField('$.timestamp', as_name='timestamp', sortable=True),
        TextField('$.kind', as_name='kind')
    ), definition=IndexDefinition(prefix=[_key_trade('','')[0:-1]], index_type=IndexType.JSON))

    return idx


def index_transaction(redis:Redis):
    idx = redis.ft(_key_transaction('idx', '', '')[0:-2].lower())
    try:
        idx.info()
        return idx
    except ResponseError:
        pass

    idx.create_index((
        TextField('$.account', as_name='account'),
        NumericField('$.timestamp', as_name='timestamp', sortable=True),
        TextField('$.symbol', as_name='symbol')
    ), definition=IndexDefinition(prefix=[_key_transaction('', '', '')[0:-2]], index_type=IndexType.JSON))

    return idx

def search_assets(redis: Redis, query: str):
    idx = index_asset(redis)
    query = Query(query).paging(0, LARGE_PAGE_SIZE)
    print(_build_search_query(idx, query))
    return _deserialize_results(idx.search(query))


def set_asset(redis: Redis, symbol: str, name: str, description: str, website: str=None, 
                   sector: str=None, industry: str=None, contact_info={}, financial_info={}):
    if not sector:
        sector = ''

    if not industry:
        industry = ''

    if not website:
        website = ''

    obj = {'symbol':symbol,
           'name':name, 
           'description':description, 
           'website':website, 
           'sector':sector, 
           'industry':industry,
           'price':{'live':None, 'mock':None},
           'contact':contact_info,
           'financial':financial_info}

    redis.json().set(_key_asset(symbol), Path.rootPath(), obj)


def set_asset_live_price(redis: Redis, symbol: str, price: float):
    redis.json().set(_key_asset(symbol), '$.price.live', price)


def set_asset_mock_price(redis: Redis, symbol: str, price: float):
    redis.json().set(_key_asset(symbol), '$.price.mock', price)

def set_asset_portfolio_value(redis: Redis, account: int, symbol: str, shares: float, price: float, value: float, timestamp: int):
    obj = {'account':str(account),
           'symbol':symbol.upper(),
           'shares':shares,
           'price':price,
           'value':value,
           'timestamp':timestamp}
    
    redis.json().set(_key_portfolio_v(account, symbol, timestamp), Path.rootPath(), obj)


def set_bar(redis: Redis, symbol: str, timestamp: int, open: float,
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


def set_fund(redis: Redis, name: str, description: str, assets: list):
    id = name.replace(" ", "").lower()
    obj = {'id':id,
           'name':name,
           'description':description,
           'assets':assets}
    
    redis.json().set(_key_fund(id), Path.rootPath(), obj)


def set_trade(redis: Redis, symbol: str, price: str, timestamp: str, kind: str):
    ## TODO: kind should be an enum type thing eventually

    obj = {'symbol':symbol,
           'price':price,
           'timestamp':timestamp,
           'kind':kind}

    redis.json().set(_key_trade(symbol, timestamp), Path.rootPath(), obj)


def set_transaction(redis: Redis, account: int, timestamp: int, shares: float, symbol: str, price: float, balance: float, total_spent: float, fund: str=''):

    obj = {'account':str(account),
           'timestamp':timestamp,
           'shares':shares,
           'price':price,
           'symbol':symbol, 
           'fund':fund,
           'total_spent':total_spent,
           'balance':balance}

    redis.json().set(_key_transaction(account, symbol, timestamp), Path.rootPath(), obj)


def _build_search_query(index: SearchCommands, query: Query):
    return ' '.join([SEARCH_CMD] + list(map(str, index._mk_query_args(query, None)[0])))


def _deserialize_results(results) -> list:
    '''turn a list of json at results.docs into a list of dicts'''
    return [loads(result.json) for result in results.docs]