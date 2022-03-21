from os import environ

from cleo import Command

from redisfi.web.app import run

class ServerStart(Command):
    '''
    Start the web server

    server
        {--debug : Runs the Debug Server}
        {--r|redis-url=redis://localhost:6379 : Redis URL - can also set with REDIS_URL env var}
    '''

    def handle(self):
        debug = self.option('debug')
        redis_url = environ.get('REDIS_URL', self.option('redis-url'))
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