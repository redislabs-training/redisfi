from time import sleep
from random import triangular
from pprint import pformat
import yfinance as Y
from clikit.api.io.flags import VERY_VERBOSE, VERBOSE, DEBUG

from redisfi import db as DB
from redisfi.bridge.adapter.base import BaseAdapter

jitter = lambda: sleep(triangular(1, 3))

class YahooFinanceHistoric(BaseAdapter):
    def run(self):
        self.cli.line(f'<info>Downloading Historic Data for</info> <comment>{len(self.assets)}</comment> <info>Assets</info>')
        items = Y.download(" ".join(self.assets), group_by="ticker")
        self.cli.line(f'<info>Transforming and Loading into Redis</info>')
        progress_bar = self.cli.progress_bar(len(self.assets))
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
                        DB.set_bar(pipe, symbol, timestamp, bar.Open, bar.High, bar.Low, bar.Close, bar.Volume)
                
                pipe.execute()
                progress_bar.advance()
            progress_bar.finish()
        
        self.cli.line('') # progress bar doesn't new line when it's done