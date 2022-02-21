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
```

Once the dependancies are installed, you can use `poetry run redisfi-compose up` to start using remote containers or add the `--build` arg to build it locally.

## full
`redisfi` is the full CLI that allows access to the various components of RedisFI, see its help menu for more info.