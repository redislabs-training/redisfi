from cleo import Command

class BridgeRun(Command):
    '''
    Run's the Bridge data harvester

    run

    '''

    def handle(self):
        self.line("<error>you're a bridge</error>")
        

class BridgeBase(Command):
    '''
    Bridge commands

    bridge
    '''

    commands = [BridgeRun()]

    def handle(self):
        return self.call("help", self._config.name)
