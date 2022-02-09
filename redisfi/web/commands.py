from cleo import Command

from redisfi.web.app import run

class ServerStart(Command):
    '''
    Start the web server

    server
        {--debug : Runs the Debug Server}
    '''

    def handle(self):
        debug = self.option('debug')
        run(debug=debug)

class WebBase(Command):
    '''
    Web commands

    web
    '''

    commands = [ServerStart()]

    def handle(self):
        return self.call("help", self._config.name)