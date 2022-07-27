from json import loads

from redisfi import db as DB
from redisfi.bridge.adapter.base import BaseAdapter

class JSONFileLoader(BaseAdapter):
    files = []

    def run(self):
        for file in self.files:
            self.cli.line(f'<info>Loading file: </info><comment>{file}</comment>')
            with open(file, 'r') as f:
                self.process(loads(f.read()))

    def process(self, obj):
        raise NotImplementedError

class JSONComponentMetadataFileLoader(JSONFileLoader):
    files = ['data/components.json']

    def process(self, obj):
        for component in obj:
            DB.set_component(self.redis, **component)

class JSONMetadataFileLoader(JSONFileLoader):
    files = ['data/crypto_metadata.json']

    def process(self, obj):
        for asset in obj:
            DB.set_asset(self.redis, **asset)

class JSONPortfolioMetadataFileLoader(JSONFileLoader):
    files = ['data/portfolio.json']

    def process(self, obj):
        DB.set_portfolio(self.redis, **obj)
