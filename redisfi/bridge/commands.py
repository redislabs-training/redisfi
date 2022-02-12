from cleo import Command

from redisfi.bridge.adapter.alpaca import AlpacaAdapter

class BridgeRunAll(Command):
    '''
    Run all available adapters

    run_all
        {--H|redis-host=localhost : Redis Hostname, defaults to localhost}
        {--P|redis-port=6379 : Redis port, defaults to 6379}
    '''

    adapters = [AlpacaAdapter]

    def handle(self):
        host = self.option('redis-host')
        port = self.option('redis-port')
        redis_url = f'redis://{host}:{port}'
        _adapters = [adapter(redis_url=redis_url) for adapter in self.adapters]

        ## TODO: probably multithread/process this - early attempts were distracting
        _ = [adapter.run() for adapter in _adapters]
        
class BridgeBase(Command):
    '''
    Bridge commands

    bridge
    '''

    commands = [BridgeRunAll()]

    def handle(self):
        return self.call("help", self._config.name)
