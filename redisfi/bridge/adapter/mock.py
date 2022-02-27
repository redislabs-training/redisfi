from time import sleep
from random import gauss, shuffle, triangular

from clikit.api.io.flags import VERBOSE

from redisfi import db as DB
from redisfi.bridge.adapter.base import BaseAdapter

class RNGPriceGenerator(BaseAdapter):
    def __init__(self, asset_multiplier, crypto_multiplier, update_ticks, **kwargs) -> None:
        super().__init__(**kwargs)
        self.asset_multiplier = asset_multiplier
        self.crypto_multiplier = crypto_multiplier
        self.update_ticks = update_ticks
        
    
    def run(self):
        prices = {}
        for asset in self.assets + self.crypto:
            latest = DB.get_asset_price_historic(self.redis, asset)
            prices[asset] = latest['close']

        self.cli.line(f'<info>prices: </info><comment>{prices}</comment>')

        while True:
            shuffle(self.assets)
            shuffle(self.crypto)

            for i, asset in enumerate(self.assets):
                crypto = self.crypto[i % len(self.crypto)]
                asset_price = gauss(prices[asset], prices[asset]*self.asset_multiplier)
                crypto_price = gauss(prices[crypto], prices[crypto]*self.crypto_multiplier)
                prices[asset] = asset_price
                prices[crypto] = crypto_price

                self.cli.line(f'<info>asset: </info><comment>{asset} ({asset_price})</comment>', verbosity=VERBOSE)
                self.cli.line(f'<info>crypto: </info><comment>{crypto} ({crypto_price})</comment>', verbosity=VERBOSE)

                self.live_update(asset, {'price':asset_price})
                self.live_update(crypto, {'price':crypto_price})
                
                with self.redis.pipeline(transaction=False) as p:
                    DB.set_asset_mock_price(p, asset, asset_price)
                    DB.set_asset_mock_price(p, crypto, crypto_price)
                    p.execute()
                
                sleep(triangular(*self.update_ticks))



            
