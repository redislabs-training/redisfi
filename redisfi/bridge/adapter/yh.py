from pprint import pformat, pp

import requests

from clikit.api.io.flags import DEBUG
from redisfi import db as DB
from redisfi.bridge.adapter.base import BaseAdapter

class YHFinanceMetadata(BaseAdapter):
    def __init__(self, yh_finance_api_key:str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.api_key = yh_finance_api_key
        
    def run(self):
        with self.redis.pipeline(transaction=False) as pipe:
            for symbol in self.assets:
                self.cli.line(f'<info>Pulling metadata for </info><comment>{symbol}</comment>')
                data = self._make_request(symbol)
                contact_info = self._extract_contact_info(data['assetProfile'])
                financial_info = self._extract_financial_info(data)
                try:
                    financial_info['revenue'] = self._extract_revenue(data['earnings'])
                except KeyError:
                    financial_info['revenue'] = 0
                
                DB.set_asset(pipe, symbol, data['price']['longName'], data['assetProfile'].get('longBusinessSummary'),
                        data['assetProfile'].get('website'), data['assetProfile'].get('sector'), data['assetProfile'].get('industry'),
                        contact_info=contact_info, financial_info=financial_info)

            pipe.execute()
            
        
    def _make_request(self, symbol:str) -> dict:
        data = {}
        modules = ['price', 'assetProfile', 'summaryDetail', 'earnings']
        for module in modules:
          resp = requests.get(f'https://yfapi.net/v11/finance/quoteSummary/{symbol}?lang=en&region=US&modules={module}',
                              headers={'x-api-key': self.api_key,
                                      'accept': 'application/json'})
          # adding a check to make sure the result data exists - some of the 'earnings' are mot being returned for some symbols
          json_data = resp.json()
          quote_summary = json_data.get('quoteSummary', {})
          result = quote_summary.get('result')
          if result and isinstance(result, list) and len(result) > 0:
            data[module] = result[0].get(module, {})
          else:
            data[module] = {}
        self.cli.line(f'YHFinanceMetadata._make_request() - {symbol} - {pformat(data)}', verbosity=DEBUG)
        return data

    
    def _extract_contact_info(self, data: dict) -> dict:

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
        
        self.cli.line(f'YHFinanceMetadata._extract_contact_info() - {pformat(contact_info)}', verbosity=DEBUG)

        return contact_info

    def _extract_financial_info(self, data: dict) -> dict:
        summary_detail = data['summaryDetail']
        price = data['price']
        
        financial_info = {}
        financial_info['open'] = summary_detail['regularMarketOpen'].get('fmt', 0)
        financial_info['previous_close'] = summary_detail['regularMarketPreviousClose'].get('fmt', 0)
        financial_info['high'] = summary_detail['regularMarketDayHigh'].get('fmt', 0)
        financial_info['low'] = summary_detail['regularMarketDayLow'].get('fmt', 0)
        financial_info['market_cap'] = summary_detail['marketCap'].get('fmt', price['marketCap'].get('fmt', 0))
        financial_info['52_week_high'] = summary_detail['fiftyTwoWeekHigh']['fmt']
        financial_info['52_week_low'] = summary_detail['fiftyTwoWeekLow']['fmt']
        financial_info['50_day_average'] = summary_detail['fiftyDayAverage']['fmt']
        
        self.cli.line(f'YHFinanceMetadata._extract_financial_info() - {pformat(financial_info)}', verbosity=DEBUG)
        
        return financial_info
    
    def _extract_revenue(self, data:dict) -> str:
        yearly = data['financialsChart']['yearly']
        newest_date = 0
        revenue = ''
        
        for year in yearly:
            if year['date'] > newest_date:
                newest_date = year['date']
                revenue = year['revenue']['fmt']
                
        self.cli.line(f'YHFinanceMetadata._extract_revenue() - {pformat(revenue)}', verbosity=DEBUG)
                
        return revenue
    
        
        
if __name__ == '__main__':
    data =  {
          "maxAge": 86400,
          "earningsChart": {
            "quarterly": [
              {
                "date": "1Q2022",
                "actual": {
                  "raw": 1.52,
                  "fmt": "1.52"
                },
                "estimate": {
                  "raw": 1.43,
                  "fmt": "1.43"
                }
              },
              {
                "date": "2Q2022",
                "actual": {
                  "raw": 1.2,
                  "fmt": "1.20"
                },
                "estimate": {
                  "raw": 1.16,
                  "fmt": "1.16"
                }
              },
              {
                "date": "3Q2022",
                "actual": {
                  "raw": 1.29,
                  "fmt": "1.29"
                },
                "estimate": {
                  "raw": 1.27,
                  "fmt": "1.27"
                }
              },
              {
                "date": "4Q2022",
                "actual": {
                  "raw": 1.88,
                  "fmt": "1.88"
                },
                "estimate": {
                  "raw": 1.94,
                  "fmt": "1.94"
                }
              }
            ],
            "currentQuarterEstimate": {
              "raw": 1.43,
              "fmt": "1.43"
            },
            "currentQuarterEstimateDate": "1Q",
            "currentQuarterEstimateYear": 2023,
            "earningsDate": [
              {
                "raw": 1682506740,
                "fmt": "2023-04-26"
              },
              {
                "raw": 1682942400,
                "fmt": "2023-05-01"
              }
            ]
          },
          "financialsChart": {
            "yearly": [
              {
                "date": 2019,
                "revenue": {
                  "raw": 260174000000,
                  "fmt": "260.17B",
                  "longFmt": "260,174,000,000"
                },
                "earnings": {
                  "raw": 55256000000,
                  "fmt": "55.26B",
                  "longFmt": "55,256,000,000"
                }
              },
              {
                "date": 2020,
                "revenue": {
                  "raw": 274515000000,
                  "fmt": "274.51B",
                  "longFmt": "274,515,000,000"
                },
                "earnings": {
                  "raw": 57411000000,
                  "fmt": "57.41B",
                  "longFmt": "57,411,000,000"
                }
              },
              {
                "date": 2021,
                "revenue": {
                  "raw": 365817000000,
                  "fmt": "365.82B",
                  "longFmt": "365,817,000,000"
                },
                "earnings": {
                  "raw": 94680000000,
                  "fmt": "94.68B",
                  "longFmt": "94,680,000,000"
                }
              },
              {
                "date": 2022,
                "revenue": {
                  "raw": 394328000000,
                  "fmt": "394.33B",
                  "longFmt": "394,328,000,000"
                },
                "earnings": {
                  "raw": 99803000000,
                  "fmt": "99.8B",
                  "longFmt": "99,803,000,000"
                }
              }
            ],
            "quarterly": [
              {
                "date": "1Q2022",
                "revenue": {
                  "raw": 97278000000,
                  "fmt": "97.28B",
                  "longFmt": "97,278,000,000"
                },
                "earnings": {
                  "raw": 25010000000,
                  "fmt": "25.01B",
                  "longFmt": "25,010,000,000"
                }
              },
              {
                "date": "2Q2022",
                "revenue": {
                  "raw": 82959000000,
                  "fmt": "82.96B",
                  "longFmt": "82,959,000,000"
                },
                "earnings": {
                  "raw": 19442000000,
                  "fmt": "19.44B",
                  "longFmt": "19,442,000,000"
                }
              },
              {
                "date": "3Q2022",
                "revenue": {
                  "raw": 90146000000,
                  "fmt": "90.15B",
                  "longFmt": "90,146,000,000"
                },
                "earnings": {
                  "raw": 20721000000,
                  "fmt": "20.72B",
                  "longFmt": "20,721,000,000"
                }
              },
              {
                "date": "4Q2022",
                "revenue": {
                  "raw": 117154000000,
                  "fmt": "117.15B",
                  "longFmt": "117,154,000,000"
                },
                "earnings": {
                  "raw": 29998000000,
                  "fmt": "30B",
                  "longFmt": "29,998,000,000"
                }
              }
            ]
          },
          "financialCurrency": "USD"
        }
    
    # pp(_extract_contact_info(data['assetProfile']))
    # pp(_extract_revenue(data))