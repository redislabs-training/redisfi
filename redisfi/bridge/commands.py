from os import environ
from cleo import Command

from redisfi.bridge.adapter.alpaca import AlpacaLive, AlpacaHistoric
from redisfi.bridge.adapter.yahoo import YahooFinanceEnrich, YahooFinanceHistoric

class BridgeMixin:
    ## there is circular logic in importing subcommands into the base and subclassing 
    ## the same base.  this allows for shared methods without subclassing the base command

    adapters = []

    def handle(self: Command):
        adapter_config = self._adapter_config()
        _adapters = [adapter(**adapter_config) for adapter in self.adapters]

        self.line(f'<info>Starting</info> <comment>{len(_adapters)}</comment> <info>adapter{"s" if len(_adapters) > 1 else ""}</info>')
        ## TODO: multithread/process this - early attempts were distracting
        _ = [adapter.run() for adapter in _adapters]
        

    def _adapter_config(self: Command) -> dict:
        ## options from the BridgeBase can be extracted here, anything 
        ## specific to the method itself should be extracted as a 
        ## subclass with: `adapter_config = super()._adapter_config(self)` first

        host = environ.get('REDIS_HOST')
        if host is None:
            host = self.option('redis-host')
        port = environ.get('REDIS_PORT')
        if port is None:
            port = self.option('redis-port')

        adapter_config = {'cli':self, 'redis_url':f'redis://{host}:{port}'}
        self.line(f'<info>Redis URL:</info> <comment>{adapter_config["redis_url"]}</comment>')

        adapter_config['assets'] = self.option('assets').split(',')
        adapter_config['crypto'] = self.option('crypto').split(',')
        self.line(f'<info>Assets:</info> <comment>{" ".join(adapter_config["assets"])}</comment>')
        self.line(f'<info>Crypto:</info> <comment>{" ".join(adapter_config["crypto"])}</comment>')
        
        return adapter_config


class BridgePriceHistoric(BridgeMixin, Command):
    '''
    Run historic price data collection ingest

    historic
        {--hourly=1 : Number of years to extract hourly data}
    '''

    adapters = [AlpacaHistoric, YahooFinanceHistoric]

    def _adapter_config(self: Command) -> dict:
        adapter_config =  super()._adapter_config()
        adapter_config['hourly'] = int(self.option('hourly'))
        return adapter_config

class BridgeEnrich(BridgeMixin, Command):
    '''
    Run company metadata data ingest 

    enrich
    '''

    adapters = [YahooFinanceEnrich]

class BridgePriceLive(BridgeMixin, Command):
    '''
    Run live data bridge to stream active transactions

    live
    '''

    adapters = [AlpacaLive]

class BridgeBase(Command):
    '''
    Bridge commands

    bridge
        {--H|redis-host=localhost : Redis hostname - can also set with REDIS_HOST env var}
        {--P|redis-port=6379 : Redis port - can also set with REDIS_PORT env var}
        {--s|assets=GOOG,MSFT,TSLA,SPY,QQQ,PIMIX : Comma delimited list of asset symbols to track}
        {--c|crypto=BTCUSD,ETHUSD : Comma delimited list of crypto to track}
    '''

    commands = [BridgePriceLive(), BridgePriceHistoric(), BridgeEnrich()]

    def handle(self):
        return self.call("help", self._config.name)

