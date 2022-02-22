from json import loads

from redisfi import db as DB
from redisfi.bridge.adapter.base import BaseAdapter

class FileLoader(BaseAdapter):
    files = []

    def run(self):
        for file in self.files:
            self.cli.line(f'<info>Loading file: </info><comment>{file}</comment>')
            with open(file, 'r') as f:
                self.process(f.read())

    def process(self, data):
        raise NotImplementedError

class JSONMetadataFileLoader(FileLoader):
    files = ['data/crypto_metadata.json']

    def process(self, data):
        obj = loads(data)
        for asset in obj:
            DB.set_asset_json(self.redis, **asset)
