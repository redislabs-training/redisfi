from json import dumps
import requests

from cleo import Command

api_url = lambda host, path: f'https://{host}:9443/{path}'

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
        requests.packages.urllib3.disable_warnings()
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

def create_db(host, username, password, db_name, db_size, db_port, db_modules=None):
    '''
    Creates a Redis database using the Redis Enterprise REST API

    INPUTS
    host: hostname of redis-enterprise instance (foo.com)
    username: admin username (test@test.com)
    password: admin password
    db_name: name to represent the DB in the UI
    db_size: database size in bytes
    db_port: port the db is served on (typically 10000-19999)
    db_modules: a list of dicts of modules to be included in the db - defaults to None

    OUTPUTS
    tuple - (http response code, http response text)
    '''
    path = 'v1/bdbs'
    headers, data = _create_db_payload(db_name, db_size, db_port, db_modules)

    db_create_resp = requests.post(
        api_url(host, path),
        auth=(username, password),
        headers=headers,
        data=data,
        verify=False)

    return db_create_resp.status_code, db_create_resp.text

def _create_db_payload(db_name, db_size, db_port, db_modules):
    '''
    creates the JSON string for the create_db http request

    INPUTS
    db_name: name to represent the DB in the UI
    db_size: database size in bytes
    db_port: port the db is served on (typically 10000-19999)
    db_modules: a list of dicts of modules to be included in the db

    OUTPUTS
    tuple - (header dict, payload json string)
    '''
    
    assert db_modules is None or (db_modules 
                                  and type(db_modules) == list
                                  and type(db_modules[0]) == dict)
    
    payload = { "name": db_name,
                "memory_size": db_size,
                "type": "redis",
                "port": db_port
              }

    if db_modules is not None:
        payload['module_list'] = db_modules

    return {'Content-type': 'application/json'}, dumps(payload)
