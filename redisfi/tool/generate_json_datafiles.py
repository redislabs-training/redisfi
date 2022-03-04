from json import dumps

from cleo import Command

ACCOUNT = 710

class GeneratePortfolioJSONTool(Command):
    '''
    Create the data/portfoio.json file.  This is required to render the Portfolio Overview Page

    generate_portfolio_json
        {--s|stocks=SPCE,210.AMC,400.SOFI,250 : stocks for the portfolio - pipe delimited, symbol,shares_owned.symbol,shares_owned etc}
        {--e|etfs=QQQ,75.SPY,250 : ETFss for the portfolio - pipe delimited, symbol,shares_owned.symbol,shares_owned etc}
        {--r|retire=retire2050 : retirement fund for the portfolio - only 1 - must be in data/funds.json}
        {--c|crypto=ETHUSD,20 : crypto for the portfolio - pipe delimited, symbol,amount_owned.symbol,amount_owned etc }
    '''

    def handle(self):
        portfolio = {}
        portfolio['account'] = ACCOUNT
        portfolio['stocks'] = self._deserialize_input(self.option('stocks'))
        portfolio['etfs'] =  self._deserialize_input(self.option('etfs'))
        portfolio['retire'] = self.option('retire')
        portfolio['crypto'] =  self._deserialize_input(self.option('crypto'))

        with open('data/portfolio.json', 'w') as f:
            f.write(dumps(portfolio))

    def _deserialize_input(self, input: str):
        
        inputs = input.split('.')
        output = {}
        

        for _input in inputs:
            symbol, shares_owned = _input.split(',')
            output[symbol] = int(shares_owned)

        return output


        