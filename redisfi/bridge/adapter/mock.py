from datetime import datetime, timedelta
from time import sleep
from random import gauss, shuffle, triangular
from pprint import pp

from clikit.api.io.flags import VERBOSE

from redisfi import db as DB
from redisfi.bridge.adapter.base import BaseAdapter

DAYS_IN_YEAR = 365.26

class TransactionGenerator(BaseAdapter):
    def __init__(self, years_to_generate: float, interval: int, amount_to_invest_per_interval: float, account=710, fund='retire2050', **kwargs):
        super().__init__(**kwargs)
        self.years_to_generate = years_to_generate
        self.interval = timedelta(weeks=interval)
        self.amount_to_invest_per_interval = amount_to_invest_per_interval
        self.account = account
        self.fund_data = DB.get_fund(self.redis, fund)

    def run(self):
        moment = datetime.utcnow() - timedelta(days=DAYS_IN_YEAR*self.years_to_generate) 
        balances, total_spent = {}, {}
        
        with self.redis.pipeline(transaction=False) as pipe:
            while moment <= datetime.utcnow():
                timestamp = int(moment.timestamp())
                for symbol, percentage in self.fund_data['assets'].items():
                    bar = DB.get_asset_history(self.redis, symbol, end=timestamp, page=(0, 1))[0]
                    price = bar['close'] 
                    amount_to_spend = self.amount_to_invest_per_interval * percentage
                    shares = amount_to_spend / price
                    balances[symbol] = shares + balances.get(symbol, 0)
                    total_spent[symbol] = amount_to_spend + total_spent.get(symbol, 0)

                    DB.set_transaction(pipe, self.account, timestamp, shares, symbol, price, balances[symbol], total_spent[symbol], self.fund_data['id'])

                    self.cli.line(f'<info>timestamp:</info> <comment>{timestamp}</comment><info> | price: </info><comment>{price}</comment><info> | shares: </info><comment>{shares}</comment><info> | balance: </info><comment>{balances[symbol]}</comment>', verbosity=VERBOSE)
                
                pipe.execute()
                moment = moment + self.interval

class TransactionPriceMapper(BaseAdapter):
    def __init__(self, account=710, **kwargs) -> None:
        super().__init__(**kwargs)
        self.account = account

    def run(self):
        raw_transactions = DB.get_transactions(self.redis)
        transformed_transactions = {}
        for transaction in raw_transactions:
            if not transaction['symbol'] in transformed_transactions:
                transformed_transactions[transaction['symbol']] = []
            
            transformed_transactions[transaction['symbol']].insert(0, (transaction['timestamp'], transaction['balance']))

        
        for symbol, transactions in transformed_transactions.items():
            bars = DB.get_asset_history(self.redis, symbol, asc=True)
            beginning_transaction, end_transaction = transactions[0], transactions[1]
            _, shares = beginning_transaction
            end, next_shares = end_transaction
            counter = 1
            
            with self.redis.pipeline(transaction=False) as pipe:
                for bar in bars:
                    if bar['timestamp'] > end:
                        counter += 1
                        if counter < len(transactions):
                            new_end = transactions[counter]
                        else:
                            new_end = (float('inf'), next_shares) 
                        
                        shares = next_shares
                        end, next_shares = new_end
                    
                    price = (bar['high'] + bar['low']) / 2
                    
                    DB.set_asset_portfolio_value(pipe, bar['symbol'], self.account, shares, price, price * shares, bar['timestamp'])
                
                pipe.execute()


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

                timestamp = int(datetime.utcnow().timestamp())
                self.mock_trade_update(asset, {'price':asset_price, 'timestamp':timestamp})
                self.mock_trade_update(crypto, {'price':crypto_price, 'timestamp':timestamp})
                
                with self.redis.pipeline(transaction=False) as p:
                    DB.set_asset_mock_price(p, asset, asset_price)
                    DB.set_asset_mock_price(p, crypto, crypto_price)
                    p.execute()
                
                sleep(triangular(*self.update_ticks))



            
