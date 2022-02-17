import yfinance as Y
from clikit.api.io.flags import VERY_VERBOSE

from redisfi import db as DB
from redisfi.bridge.adapter.base import BaseAdapter


class YahooFinanceHistoric(BaseAdapter):
    def run(self):
        self.cli.line(f'<info>Downloading Historic Data for</info> <comment>{len(self.us_stocks)}</comment> <info>Stocks</info>')
        items = Y.download(" ".join(self.us_stocks), group_by="ticker")
        with self.redis.pipeline(transaction=False) as pipe:
            for symbol in self.us_stocks:
                rows = items[symbol].iterrows()
                for row in rows:
                    timestamp = row[0].timestamp()
                    bar = row[1]
                    DB.set_bar(pipe, symbol, timestamp, bar.Open, bar.High, bar.Low, bar.Close, bar.Volume)
                pipe.execute()

class YahooFinanceEnrich(BaseAdapter):
    def __init__(self, **kwargs) -> None:
        super().__init__( **kwargs)
        DB.index_stock_json(self.redis)

    def run(self):
        tickers = Y.Tickers(' '.join(self.us_stocks))
        with self.redis.pipeline(transaction=False) as pipe:
            for symbol, cursor in tickers.tickers.items():
                info = cursor.info
                self.cli.line(str(info), verbosity=VERY_VERBOSE)
                DB.set_stock_json(pipe, symbol, info['longName'], info['longBusinessSummary'],
                                  info['website'], info['sector'], info['industry'])

            pipe.execute()
                # import pdb; pdb.set_trace()
