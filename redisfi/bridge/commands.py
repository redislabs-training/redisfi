from os import environ
from subprocess import Popen

from cleo import Command

from redisfi.bridge.adapter.alpaca import AlpacaLive, AlpacaHistoric
from redisfi.bridge.adapter.yahoo import YahooFinanceMetadata, YahooFinanceHistoric
from redisfi.bridge.adapter.file import JSONMetadataFileLoader, JSONFundMetadataFileLoader, JSONPortfolioMetadataFileLoader
from redisfi.bridge.adapter.mock import RNGPriceGenerator, TransactionGenerator, TransactionPriceMapper


class BridgeMixin:
    ## there is circular logic in importing subcommands into the base and subclassing 
    ## the same base.  this allows for shared methods without subclassing the base command

    adapters = []

    def handle(self: Command):
        adapter_config = self._adapter_config()
        _adapters = [adapter(**adapter_config) for adapter in self.adapters]

        self.line(f'<info>Configured</info> <comment>{len(_adapters)}</comment> <info>adapter{"s" if len(_adapters) > 1 else ""}</info>')
        ## TODO: multithread/process this - early attempts were distracting
        _ = [adapter.run() for adapter in _adapters]
        

    def _adapter_config(self: Command) -> dict:
        ## options from the BridgeBase can be extracted here, anything 
        ## specific to the method itself should be extracted as a 
        ## subclass with: `adapter_config = super()._adapter_config(self)` first

        redis_url = environ.get('REDIS_URL', self.option('redis-url'))

        adapter_config = {'cli':self, 'redis_url':redis_url}
        self.line(f'<info>Redis URL:</info> <comment>{adapter_config["redis_url"]}</comment>')

        adapter_config['assets'] = self.option('assets').split(',')
        adapter_config['crypto'] = self.option('crypto').split(',')
        
        self.line(f'<info>Assets:</info> <comment>{" ".join(adapter_config["assets"])}</comment>')
        self.line(f'<info>Crypto:</info> <comment>{" ".join(adapter_config["crypto"])}</comment>')
        
        return adapter_config


class MockMixin(BridgeMixin):
    mock_adapters = []

    def handle(self):
        if environ.get('MOCK', self.option('mock')):
            self.line('<error>Enabling mock adapters</error>')
            self.adapters = self.mock_adapters
        
        super().handle()

class BridgeMetadata(BridgeMixin, Command):
    '''
    Run company metadata data ingest 

    metadata
    '''

    adapters = [JSONFundMetadataFileLoader, JSONMetadataFileLoader, JSONPortfolioMetadataFileLoader, YahooFinanceMetadata]


class BridgePriceHistoric(BridgeMixin, Command):
    '''
    Run historic price data collection ingest

    historic
        {--hourly=1 : Number of days to extract hourly data}
        {--crypto-days=365 : Number of days to extract crypto daily data}
    '''

    adapters = [AlpacaHistoric, YahooFinanceHistoric]

    def _adapter_config(self: Command) -> dict:
        adapter_config =  super()._adapter_config()
        adapter_config['hourly'] = int(self.option('hourly'))
        adapter_config['crypto_days'] = int(self.option('crypto-days'))
        return adapter_config


class BridgePriceLive(MockMixin, Command):
    '''
    Run live data bridge to stream active transactions

    live
        {--mock : Launch mock price updates instead of live}
        {--mock-asset-random-price-range=.001 : Multiplier to determine range for assets (base_price*multiplier = gaussian std deviation) - bigger means more erratic random prices}
        {--mock-crypto-random-price-range=.00001 : Multiplier to determine range for crypto (base_price*multiplier = gaussian std deviation) - bigger means more erratic random prices}
        {--mock-update-price-ticks=.25,.5 : Update prices randomly min_seconds,max_seconds }
    '''

    adapters = [AlpacaLive]
    mock_adapters = [RNGPriceGenerator]

    def _adapter_config(self: Command) -> dict:
        adapter_config = super()._adapter_config()

        if environ.get('MOCK', self.option('mock')):
            adapter_config['asset_multiplier'] = float(self.option('mock-asset-random-price-range'))
            adapter_config['crypto_multiplier'] = float(self.option('mock-crypto-random-price-range'))
            adapter_config['update_ticks'] = [float(tick) for tick in self.option('mock-update-price-ticks').split(',')]
        
        return adapter_config

class BridgePortfolioGenerator(BridgeMixin, Command):
    '''
    Generate the Portfolio and Transaction Data

    portfolio
        {--years-to-generate=5 : Number of years to generate transaction data for}
        {--interval=2 : Generate a transaction every n weeks}
        {--amount-to-invest=300 : Amount to invest each interval}
    '''

    adapters = [TransactionGenerator, TransactionPriceMapper]
    #adapters = [TransactionPriceMapper]

    def _adapter_config(self: Command) -> dict:
        adapter_config = super()._adapter_config()
        adapter_config['years_to_generate'] = float(self.option('years-to-generate'))
        adapter_config['interval'] = int(self.option('interval'))
        adapter_config['amount_to_invest_per_interval'] = float(self.option('amount-to-invest'))

        return adapter_config


class BridgeUp(Command):
    '''
    Run the whole bridge suite.  Metadata > History > Transactions > Live

    up
        {--hourly=1 : Number of days to extract hourly data}
        {--mock : Launch mock price updates instead of live}
        {--mock-asset-random-price-range=.001 : Multiplier to determine range for assets (base_price*multiplier = gaussian std deviation)}
        {--mock-crypto-random-price-range=.00001 : Multiplier to determine range for crypto (base_price*multiplier = gaussian std deviation)}
        {--mock-update-price-ticks=.25,.5 : Update prices randomly min_seconds,max_seconds }
        {--years-to-generate=5 : Number of years to generate transaction data for}
        {--interval=2 : Generate a transaction every n weeks}
        {--amount-to-invest=300 : Amount to invest each interval}
    '''

    def handle(self):
        
        global_args = ['--redis-url', environ.get('REDIS_URL', self.option('redis-url'))]
        global_args.extend(['--assets', self.option('assets')])
        global_args.extend(['--crypto', self.option('crypto')])
        
        with Popen(['poetry', 'run', 'redisfi', 'bridge', 'metadata', '--ansi'] + global_args) as p:
            p.communicate()
            if p.returncode != 0:
                return p.returncode

        historic_args = ['--hourly', self.option('hourly')]
        with Popen(['poetry', 'run', 'redisfi', 'bridge', 'historic'] + historic_args + global_args) as p:
            p.communicate()
            if p.returncode != 0:
                return p.returncode

        
        portfolio_args = ['--years-to-generate', self.option('years-to-generate')]
        portfolio_args.extend(['--interval', self.option('interval')])
        portfolio_args.extend(['--amount-to-invest', self.option('amount-to-invest')])

        with Popen(['poetry', 'run', 'redisfi', 'bridge', 'portfolio'] + portfolio_args + global_args) as p:
            p.communicate()
            if p.returncode != 0:
                return p.returncode
        
        if environ.get('MOCK', self.option('mock')):
            self.line('<error>Mock Setting Detected! - Mock adapters will be enabled</error>')
            live_args = ['--mock']
        else:
            live_args = []
             
        live_args.extend(['--mock-asset-random-price-range', self.option('mock-asset-random-price-range')])
        live_args.extend(['--mock-crypto-random-price-range', self.option('mock-crypto-random-price-range')])
        live_args.extend(['--mock-update-price-ticks', self.option('mock-update-price-ticks')])

        with Popen(['poetry', 'run', 'redisfi', 'bridge', 'live'] + live_args + global_args) as p:
            p.communicate()
            if p.returncode != 0:
                return p.returncode


    
class BridgeBase(Command):
    '''
    Bridge commands

    bridge
        {--r|redis-url=redis://localhost:6379 : Redis url - can also set with REDIS_URL env var}
        {--s|assets=GOOG,MSFT,TSLA,SNAP,GME,AMC,JPM,F,VMW,SOFI,SPCE,AMZN,SPY,QQQ,PIMIX,VEMIX,VOO,EQIX,VTI,ARKK : Comma delimited list of asset symbols to track}
        {--c|crypto=BTCUSD,ETHUSD : Comma delimited list of crypto to track}
    '''

    commands = [BridgePriceLive(), BridgePriceHistoric(), BridgeMetadata(), BridgeUp(), BridgePortfolioGenerator()]

    def handle(self):
        return self.call("help", self._config.name)

