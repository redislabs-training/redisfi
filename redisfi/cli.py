from cleo import Application

from redisfi.bridge.commands import BridgeBase

def run():
    app = Application(name='redisfi')
    app.add(BridgeBase())
    app.run()

