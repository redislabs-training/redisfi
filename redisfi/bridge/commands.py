from cleo import Command

from redisfi.bridge.adapter.alpaca import AlpacaAdapter

class BridgeLive(Command):
    '''
    Run live data bridge to stream active transactions

    live
    '''

    adapters = [AlpacaAdapter]

    def handle(self):
        host = self.option('redis-host')
        port = self.option('redis-port')
        adapter_config = {'cli':self, 'redis_url':f'redis://{host}:{port}'}
        self.line(f'<info>Redis URL:</info> <comment>{adapter_config["redis_url"]}</comment>')

        adapter_config['us_stocks'] = self.option('us-stocks').split(',')
        adapter_config['crypto'] = self.option('crypto').split(',')
        self.line(f'<info>US Stocks:</info> <comment>{" ".join(adapter_config["us_stocks"])}</comment>')
        self.line(f'<info>Crypto:</info> <comment>{" ".join(adapter_config["crypto"])}</comment>')

        _adapters = [adapter(**adapter_config) for adapter in self.adapters]

        ## TODO: probably multithread/process this - early attempts were distracting
        self.info(f'Starting {len(_adapters)} adapter{"s" if len(_adapters) > 1 else ""}')
        _ = [adapter.run() for adapter in _adapters]
        
class BridgeBase(Command):
    '''
    Bridge commands

    bridge
        {--H|redis-host=localhost : Redis Hostname}
        {--P|redis-port=6379 : Redis port}
        {--s|us-stocks=MSFT,TSLA : Comma delimited list of us stocks to track}
        {--c|crypto=BTCUSD,ETHUSD : Comma delimited list of crypto to track}
    '''

    commands = [BridgeLive()]

    def handle(self):
        return self.call("help", self._config.name)
