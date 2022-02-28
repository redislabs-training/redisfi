from datetime import datetime, timedelta

from alpaca_trade_api.rest import REST, TimeFrame, Bar
from alpaca_trade_api.stream import Stream, URL, Trade
from clikit.api.io.flags import VERBOSE, VERY_VERBOSE

from redisfi import db as DB
from redisfi.bridge.adapter.base import BaseAdapter

class AlpacaBase(BaseAdapter):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.api_key = 'PKZJJYRH8S9H7CNWJ19K'
        self.api_secret_key = 'cq0gizc7bjbiAeiXhCV3wWfT7U38xKvwgWM0AIbH'

class AlpacaLive(AlpacaBase):
    async def _crypto_trade_stream_handler(self, obj: Trade):
        obj_dict = obj.__dict__['_raw']
        obj_dict['timestamp'] = int(datetime.now().timestamp())
        self.live_trade_update(obj_dict['symbol'], obj_dict)
        self.cli.line(str(obj), verbosity=VERY_VERBOSE)
        DB.set_asset_live_price(self.redis, obj_dict['symbol'], obj_dict['price'])

    async def _stock_trade_stream_handler(self, obj: Trade):
        obj_dict = obj.__dict__['_raw']
        obj_dict['conditions'] = ','.join(obj_dict['conditions'])
        obj_dict['timestamp'] = int(datetime.now().timestamp())
        self.live_trade_update(obj_dict['symbol'], obj_dict)
        self.cli.line(str(obj), verbosity=VERBOSE)
        DB.set_asset_live_price(self.redis, obj_dict['symbol'], obj_dict['price'])
  
    def run(self):
        s = Stream(self.api_key,
                   self.api_secret_key, 
                   base_url=URL('https://paper-api.alpaca.markets'), 
                   data_feed='iex')
        s.subscribe_trades(self._stock_trade_stream_handler, *self.assets)
        s.subscribe_crypto_trades(self._crypto_trade_stream_handler, *self.crypto)

        s.run() 

class AlpacaHistoric(AlpacaBase):
    def __init__(self, hourly: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.hourly = hourly
        self.api = REST(self.api_key, self.api_secret_key, base_url=URL('https://paper-api.alpaca.markets'))

    def _bar_kwargs(self, bar: Bar):
        kwargs = {}
        kwargs['open']   = bar._raw['o']
        kwargs['high']   = bar._raw['h']
        kwargs['low']    = bar._raw['l']
        kwargs['close']  = bar._raw['c']
        kwargs['volume'] = bar._raw['v']

        return kwargs

    def _bar_timestamp(self, bar: Bar):
        return datetime.fromisoformat(bar._raw['t'][0:-1]).timestamp()
    
    def run(self):
        self.get_hourly_data()

    def get_hourly_data(self):
        from_when_dt = datetime.now() - timedelta(days=self.hourly)
        from_when = from_when_dt.isoformat().split('T')[0]

        with self.redis.pipeline(transaction=False) as pipe:
            for ticker in self.assets:
                self.cli.line(f'<info>Pulling hourly data for </info><comment>{ticker}</comment> <info>from</info> <comment>{from_when}</comment> <info>til</info> <comment>now</comment>')
                bars = self.api.get_bars_iter(ticker, TimeFrame.Hour, from_when)
                for bar in bars:
                    timestamp = self._bar_timestamp(bar)
                    DB.set_bar(pipe, ticker, timestamp, **self._bar_kwargs(bar))

                pipe.execute()
            
            for ticker in self.crypto:
                self.cli.line(f'<info>Pulling hourly data for </info><comment>{ticker}</comment> <info>from</info> <comment>{from_when}</comment> <info>til</info> <comment>now</comment>')
                bars = self.api.get_crypto_bars_iter(ticker, TimeFrame.Hour, from_when)
                for bar in bars:
                    timestamp = self._bar_timestamp(bar)
                    DB.set_bar(pipe, ticker, timestamp, **self._bar_kwargs(bar))

                pipe.execute()
                


