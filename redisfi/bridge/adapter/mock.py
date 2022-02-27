from datetime import datetime, timedelta
from time import sleep
from random import gauss, shuffle, triangular

from clikit.api.io.flags import VERBOSE

from redisfi import db as DB
from redisfi.bridge.adapter.base import BaseAdapter

DAYS_IN_YEAR = 365.26

class TransactionGenerator(BaseAdapter):
    def __init__(self, years_to_generate: float, interval: int, amount_to_invest_per_interval: float, account=710, fund='retire2050', kind='retire2050', **kwargs):
        super().__init__(**kwargs)
        self.years_to_generate = years_to_generate
        self.interval = timedelta(weeks=interval)
        self.amount_to_invest_per_interval = amount_to_invest_per_interval
        self.account = account
        self.fund_data = DB.get_fund(self.redis, fund)
        self.kind = kind

    def run(self):
        moment = datetime.now() - timedelta(days=DAYS_IN_YEAR*self.years_to_generate) 
        balance = 0
        
        while moment <= datetime.now():
            price = 0
            for symbol, percentage in self.fund_data['assets'].items():
                bar = DB.get_asset_history(self.redis, symbol, end=int(moment.timestamp()), page=(0, 1))[0]
                price += bar['close'] * percentage
                
            shares = self.amount_to_invest_per_interval / price
            balance += shares

            DB.set_transaction_json(self.redis, self.account, int(moment.timestamp()), shares, self.kind, price, balance)
            self.cli.line(f'<info>timestamp: </info><comment>{int(moment.timestamp())}</comment> <info>| price: </info><comment>{price}</comment> <info>| shares: </info><comment>{shares}</comment> <info>| balance: </info><comment>{balance}</comment>', verbosity=VERBOSE)

            moment = moment + self.interval

class RNGPriceGenerator(BaseAdapter):
    def __init__(self, asset_multiplier, crypto_multiplier, update_ticks, **kwargs) -> None:
        super().__init__(**kwargs)
        self.asset_multiplier = asset_multiplier
        self.crypto_multiplier = crypto_multiplier
        self.update_ticks = update_ticks
        
    def run(self):
        prices = {}
        for asset in self.assets + self.crypto:
            prices[asset] = DB.get_asset_price_historic(self.redis, asset)

        self.cli.line(f'<info>Prices: </info><comment>{prices}</comment>')

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



            
