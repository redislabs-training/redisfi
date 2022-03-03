# redisfi

RedisFI is an application designed to show RediSearch+JSON and Vector Similarity Search in an Investment management App.

There's a lightweight way to run RedisFI and a full way to run it.

## Prereqs
Both forms require [Python 3.9](https://stackoverflow.com/a/66907362) (not above) and [Poetry](https://python-poetry.org)

```
pip3 install poetry
```

## compose

`redisfi-compose` is a lightweight CLI really just meant to run RedisFI using Docker Containers.  If you only want to use it, you can install a smaller set of dependancies which will be faster/easier.

```
poetry install --no-dev
poetry run redisfi-compose
```

Once the dependancies are installed, you can use `poetry run redisfi-compose up` to start using remote containers or add the `--build` arg to build it locally.

## full

`redisfi` is the full CLI that allows access to the various components of RedisFI, see its help menu for more info.
```
poetry install
poetry run redisfi
```

To run locally, you need a Redis Instance.  Default is `localhost:6379`.

There are two components, a bridge and a webserver.  The bridge integrates all the external data and loads it into Redis.  You can start it with `poetry run redisfi bridge up`, which will load all the various data in the correct order and start the live price adapter. Once it's done, you can start the webserver by running `poetry run redisfi web server`.  Add `--mock` to the bridge and `--debug` to the webserver to enable more of a developer mode.
