from alpaca_trade_api.stream import Stream, URL

from redisfi.bridge.adapter.base import BaseAdapter

class AlpacaAdapter(BaseAdapter):
    def __init__(self, name='alpaca', **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.api_key = 'PKZJJYRH8S9H7CNWJ19K'
        self.api_secret_key = 'cq0gizc7bjbiAeiXhCV3wWfT7U38xKvwgWM0AIbH'

    async def _stream_handler(self, obj):
        self.write(obj.__dict__['_raw']) 
        print(obj)
        
    def run(self):
        s = Stream(self.api_key,
                   self.api_secret_key, 
                   base_url=URL('https://paper-api.alpaca.markets'), 
                   data_feed='iex')

        s.subscribe_crypto_trades(self._stream_handler, 'BTCUSD')
        # s.subscribe_crypto_trades(self._stream_handler, 'ETHUSD')
        s.run()