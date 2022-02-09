from cleo import Application

from redisfi.bridge.commands import BridgeBase
from redisfi.web.commands import WebBase

def run():
    app = Application(name='redisfi')
    app.add(BridgeBase())
    app.add(WebBase())
    app.run()

