from lib2to3.pytree import Base
import yfinance as Y

from redisfi import db as DB
from redisfi.bridge.adapter.base import BaseAdapter


class YahooFinanceHistoric(BaseAdapter):
    def run(self):
        self.cli.line(f'<info>Downloading Historic Data for</info> <comment>{len(self.us_stocks)}</comment> <info>Stocks</info>')
        items = Y.download(" ".join(self.us_stocks), group_by="ticker")
        with self.redis.pipeline() as pipe:
            for ticker in self.us_stocks:
                rows = items[ticker].iterrows()
                for row in rows:
                    timestamp = row[0].timestamp()
                    bar = row[1]
                    DB.set_bar(pipe, ticker, timestamp, bar.Open, bar.High, bar.Low, bar.Close, bar.Volume)
                pipe.execute()

class YahooFinanceEnrich(BaseAdapter):
    def run(self):
        pass
