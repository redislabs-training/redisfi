import yfinance as Y
from clikit.api.io.flags import VERY_VERBOSE

from redisfi import db as DB
from redisfi.bridge.adapter.base import BaseAdapter

class YahooFinanceHistoric(BaseAdapter):
    def run(self):
        self.cli.line(f'<info>Downloading Historic Data for</info> <comment>{len(self.assets)}</comment> <info>Assets</info>')
        items = Y.download(" ".join(self.assets), group_by="ticker")
        with self.redis.pipeline(transaction=False) as pipe:
            for symbol in self.assets:
                rows = items[symbol].iterrows()
                for row in rows:
                    timestamp = row[0].timestamp()
                    bar = row[1]
                    ## we only accept FULL bars, meaning each value exists - when we pull historic data in bulk
                    ## we get a bunch of extra NaN's to round out the table, this checks to make sure each
                    ## one isn't a NaN. Why they can't resolve to False or None? ¯\_(ツ)_/¯
                    if all(map(lambda x: str(x) != 'nan', (bar.Open, bar.High, bar.Low, bar.Close, bar.Volume))):
                        self.cli.line(str(bar), verbosity=VERY_VERBOSE)
                        DB.set_bar_json(pipe, symbol, timestamp, bar.Open, bar.High, bar.Low, bar.Close, bar.Volume)
                
                pipe.execute()

class YahooFinanceEnrich(BaseAdapter):
    def run(self):
        tickers = Y.Tickers(' '.join(self.assets))
        with self.redis.pipeline(transaction=False) as pipe:
            for symbol, cursor in tickers.tickers.items():
                info = cursor.info
                self.cli.line(str(info), verbosity=VERY_VERBOSE)
                DB.set_stock_json(pipe, symbol, info['longName'], info['longBusinessSummary'],
                                  info.get('website', ''), info.get('sector', ''), info.get('industry', ''))

            pipe.execute()
                # import pdb; pdb.set_trace()
