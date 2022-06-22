from gevent import monkey
monkey.patch_all()

from cleo import Application

from redisfi.compose import DeployCommand, UpCommmand
from redisfi.bridge.commands import BridgeBase
from redisfi.web.commands import WebBase
from redisfi.tool.commands import ToolBase

def run():
    app = Application(name='redisfi')
    app.add(BridgeBase())
    app.add(WebBase())
    app.add(ToolBase())
    app.add(UpCommmand())
    app.add(DeployCommand())
    app.run()

