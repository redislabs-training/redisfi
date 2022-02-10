from alpaca_trade_api.stream import Stream, URL, Trade

from redisfi.bridge.adapter.base import BaseAdapter

class AlpacaAdapter(BaseAdapter):
    def __init__(self, name='alpaca', **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.api_key = 'PKZJJYRH8S9H7CNWJ19K'
        self.api_secret_key = 'cq0gizc7bjbiAeiXhCV3wWfT7U38xKvwgWM0AIbH'

    async def _crypto_trade_stream_handler(self, obj: Trade):
        obj_dict = obj.__dict__['_raw']
        name = f'trades:{obj_dict["exchange"]}:{obj_dict["symbol"]}'
        self.write(obj_dict, name=name) 
        print(obj)

    async def _stock_trade_stream_handler(self, obj: Trade):
        print(obj)
        
    def run(self):
        s = Stream(self.api_key,
                   self.api_secret_key, 
                   base_url=URL('https://paper-api.alpaca.markets'), 
                   data_feed='iex')
        # s.subscribe_trades(self._stock_trade_stream_handler, 'TSLA', 'appl', 'msft')  ## TODO: Test when markets are open
        s.subscribe_crypto_trades(self._crypto_trade_stream_handler, 'BTCUSD')
        s.subscribe_crypto_trades(self._crypto_trade_stream_handler, 'ETHUSD')
        s.run()