from cleo import Command

from redisfi.tool.create_db import CreateDBTool

class ToolBase(Command):
    '''
    Utility commands

    tool
    '''

    commands = [CreateDBTool()]

    def handle(self):
        return self.call("help", self._config.name)

