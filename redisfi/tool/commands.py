from cleo import Command

from redis import Redis

from redisfi.tool.create_db import create_db
from redisfi.tool.generate_json_datafiles import GeneratePortfolioJSONTool

class FlushNamespace(Command):
    '''
    Delete all the keys that match the string provided

    flush_namespace
        {namespace : Pattern to delete}
        {--H|redis-host=localhost : Redis Hostname - can also set with REDIS_HOST env var}
        {--P|redis-port=6379 : Redis port - can also set with REDIS_PORT env var}}
    '''

    def handle(self):
        namespace = self.argument('namespace')
        host = self.option('redis-host')
        port = self.option('redis-port')

        r = Redis(host=host, port=port)
        info = r.info('keyspace')
        keys = r.keys(namespace)

        self.line(f'{len(keys)} found! {100 * (len(keys)/info["db0"]["keys"])} % of total keyspace')

        if len(keys) == 0:
            return

        yes = self.confirm('Are you sure you want to delete?')

        if yes: 
            r.delete(*keys)


class CreateDBTool(Command):
    '''
    Creates a Redis Database with Search+JSON for RedisFI

    create_db
        {--H|--host=localhost : Location of the Redis Enterprise Cluster}
        {--u|--user=test@test.com : Redis Enterprise REST API User}
        {--p|--password=test : Redis Enterprise REST API Password}
        {--N|--name=redisfi : Name to create the DB with}
        {--s|--size=104857600 : DB Size, defaults to 100MB}
        {--P|--port=6379 : Port to create the DB on}
    '''

    def handle(self):
        
        module_list = [{
                "module_id": "668efa9d03113f525f556662ec2b3e88",
                "module_name": "search",
                "semantic_version": "99.99.99",
                "module_args": "PARTITIONS AUTO"},
                {"module_id": "92bbd20c4e39e68425fd887c1367c13d",
                "module_name": "ReJSON",
                "semantic_version": "99.99.99",
                "module_args":""}]

        host = self.option('host')
        user = self.option('user')
        password = self.option('password')
        name = self.option('name')
        size = int(self.option('size'))
        port = int(self.option('port'))
        self.info(f'Creating DB {name} on cluster at {host} on port {port}')
        status, text = create_db(host, user, password, name, size, port, module_list)
        if status == 200:
            self.info('DB created!')
        else:
            self.line_error(f'Error creating DB: {text}', style='error')

class ToolBase(Command):
    '''
    Utility commands

    tool
    '''

    commands = [CreateDBTool(), FlushNamespace(), GeneratePortfolioJSONTool()]

    def handle(self):
        return self.call("help", self._config.name)

