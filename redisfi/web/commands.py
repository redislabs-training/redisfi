from os import environ

from cleo import Command

from redisfi.web.app import run

class ServerStart(Command):
    '''
    Start the web server

    server
        {--debug : Runs the Debug Server}
        {--H|redis-host=localhost : Redis Hostname}
        {--P|redis-port=6379 : Redis port}
    '''

    def handle(self):
        debug = self.option('debug')
        host = self.option('redis-host')
        port = self.option('redis-port')
        redis_url = f'redis://{host}:{port}'
        self.line(f'<info>Redis URL:</info> <comment>{redis_url}</comment>')
        run(debug=debug, redis_url=redis_url)

class WebBase(Command):
    '''
    Web commands

    web
    '''

    commands = [ServerStart()]

    def handle(self):
        return self.call("help", self._config.name)