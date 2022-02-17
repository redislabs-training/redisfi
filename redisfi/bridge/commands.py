from cleo import Command

from redisfi.bridge.adapter.alpaca import AlpacaLive, AlpacaHistoric

class BridgeMixin:
    ## there is circular logic in importing subcommands into the base and subclassing 
    ## the same base.  this allows for shared methods without subclassing the base command

    adapters = []

    def handle(self):
        adapter_config = self._adapter_config()
        _adapters = [adapter(**adapter_config) for adapter in self.adapters]

        self.info(f'Starting {len(_adapters)} adapter{"s" if len(_adapters) > 1 else ""}')
        ## TODO: multithread/process this - early attempts were distracting
        _ = [adapter.run() for adapter in _adapters]
        

    def _adapter_config(self: Command) -> dict:
        ## options from the BridgeBase can be extracted here, anything 
        ## specific to the method itself should be extracted as a 
        ## subclass with: `adapter_config = super()._adapter_config(self)` first

        host = self.option('redis-host')
        port = self.option('redis-port')
        adapter_config = {'cli':self, 'redis_url':f'redis://{host}:{port}'}
        self.line(f'<info>Redis URL:</info> <comment>{adapter_config["redis_url"]}</comment>')

        adapter_config['us_stocks'] = self.option('us-stocks').split(',')
        adapter_config['crypto'] = self.option('crypto').split(',')
        self.line(f'<info>US Stocks:</info> <comment>{" ".join(adapter_config["us_stocks"])}</comment>')
        self.line(f'<info>Crypto:</info> <comment>{" ".join(adapter_config["crypto"])}</comment>')
        
        return adapter_config


class BridgeHistoric(BridgeMixin, Command):
    '''
    Run historic data collection ingest

    historic
        {--hourly=1 : Number of years to extract hourly data}
        {--daily=100 : Number of years to extract daily data}
    '''

    adapters = [AlpacaHistoric]

    def _adapter_config(self: Command) -> dict:
        adapter_config =  super()._adapter_config()
        adapter_config['hourly'] = int(self.option('hourly'))
        adapter_config['daily'] = int(self.option('daily'))
        return adapter_config

class BridgeLive(BridgeMixin, Command):
    '''
    Run live data bridge to stream active transactions

    live
    '''

    adapters = [AlpacaLive]


class BridgeBase(Command):
    '''
    Bridge commands

    bridge
        {--H|redis-host=localhost : Redis hostname}
        {--P|redis-port=6379 : Redis port}
        {--s|us-stocks=MSFT,TSLA : Comma delimited list of us stocks to track}
        {--c|crypto=BTCUSD,ETHUSD : Comma delimited list of crypto to track}
    '''

    commands = [BridgeLive(), BridgeHistoric()]

    def handle(self):
        return self.call("help", self._config.name)

