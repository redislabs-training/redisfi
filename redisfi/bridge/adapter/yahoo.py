from pprint import pformat, pp
import yfinance as Y
from clikit.api.io.flags import VERY_VERBOSE, VERBOSE

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

class YahooFinanceMetadata(BaseAdapter):
    def run(self):
        tickers = Y.Tickers(' '.join(self.assets))
        with self.redis.pipeline(transaction=False) as pipe:
            for symbol, cursor in tickers.tickers.items():
                self.cli.line(f'<info>Pulling data for </info><comment>{symbol}</comment>')
                data: dict = cursor.info
                self.cli.line(pformat(data, sort_dicts=True), verbosity=VERBOSE)
                contact_info = self._extract_contact_info(data)
                financial_info = self._extract_financial_info(data)
                DB.set_asset_json(pipe, symbol, data['longName'], data['longBusinessSummary'],
                                  data.get('website'), data.get('sector'), data.get('industry'),
                                  contact_info=contact_info, financial_info=financial_info)

            pipe.execute()
                
    def _extract_contact_info(self, data: dict):
        contact_info = {}
        contact_info['addr1'] = data.get('address1', '')
        contact_info['addr2'] = data.get('address2', '')
        contact_info['addr3'] = data.get('address3')
        contact_info['city'] = data.get('city', '')
        contact_info['state'] = data.get('state', '')
        contact_info['zip'] = data.get('zip', '')
        contact_info['country'] = data.get('country', '')
        
        if contact_info['addr3'] is None:
            contact_info['addr3'] = f'{contact_info["city"]}{"," if contact_info["city"] else ""} {contact_info["state"]} {contact_info["zip"]}'

        contact_info['phone'] = data.get('phone', '')
        
        self.cli.line(pformat(contact_info, sort_dicts=True), verbosity=VERY_VERBOSE)

        return contact_info
    
    def _extract_financial_info(self, data: dict):
        financial_info = {}
        financial_info['open'] = data['regularMarketOpen']
        financial_info['previous_close'] = data['regularMarketPreviousClose']
        financial_info['high'] = data['regularMarketDayHigh']
        financial_info['low'] = data['regularMarketDayLow']
        financial_info['market_cap'] = data['marketCap']
        financial_info['recommendation'] = data.get('recommendationKey', '')
        financial_info['revenue'] = data.get('totalRevenue', 0)
        financial_info['52_week_high'] = data['fiftyTwoWeekHigh']
        financial_info['52_week_low'] = data['fiftyTwoWeekLow']
        financial_info['50_day_average'] = data['fiftyDayAverage']
        
        self.cli.line(pformat(financial_info, sort_dicts=True), verbosity=VERY_VERBOSE)
        
        return financial_info