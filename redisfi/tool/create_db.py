from json import dumps
import requests
requests.packages.urllib3.disable_warnings()

api_url = lambda host, path: f'https://{host}:9443/{path}'

def create_db(host, username, password, db_name, db_size, db_port, shard_count, db_modules=None):
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
    headers, data = _create_db_payload(db_name, db_size, db_port, db_modules, shard_count)

    db_create_resp = requests.post(
        api_url(host, path),
        auth=(username, password),
        headers=headers,
        data=data,
        verify=False)

    return db_create_resp.status_code, db_create_resp.text

def _create_db_payload(db_name, db_size, db_port, db_modules, shard_count):
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
                "port": db_port,
                "sharding":True,
                "shards_count":shard_count,
              }

    if db_modules is not None:
        payload['module_list'] = db_modules

    return {'Content-type': 'application/json'}, dumps(payload)
