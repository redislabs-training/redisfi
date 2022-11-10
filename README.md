# redisfi

RedisFI is an application designed to show RediSearch+JSON and Vector Similarity Search in an Investment management App.

There's a lightweight way to run RedisFI and a full way to run it.

## Prereqs
Both forms require [Python 3.9](https://stackoverflow.com/a/66907362) (not above) and [Poetry](https://python-poetry.org)

```
pip3 install poetry
```
### Alpaca API
RedisFI uses Alpaca's API to gather historic and live market data.  In order to use it, you'll need to set up an account and API keys for a paper trading account.

- Navigate to [alpaca.markets](https://alpaca.markets)
- Click the Sign Up button and enter in your email and a password.
- Go to your email and click the `Confirm My Account` button.
- Login with the email/password combo from earlier
- This should take you to the `Live Trading` console.  Click the `Live Trading` drop down and click into the paper account.  This [link](https://app.alpaca.markets/paper/dashboard/overview) should take you there after you're logged in.
- On the bottom right there's a `Your API Keys` box.  Click `View` and then click the `Generate New` button.  It should show you an API key and Secret Key.  Copy those into the configuration panel below.  You can either come back here to regenerate new ones, or save those to use for future deployments. 

## compose

`redisfi-compose` is a lightweight CLI really just meant to run RedisFI using Docker Containers.  If you only want to use it, you can install a smaller set of dependancies which will be faster/easier.

```
poetry install --no-dev
poetry run redisfi-compose
```

Once the dependancies are installed, you can use `poetry run redisfi-compose up ALPACA_API_KEY ALPACA_SECRET` to start using remote containers or add the `--build` arg to build it locally.  Once running, you can access the site by going to lcoalhost:8000

## full

`redisfi` is the full CLI that allows access to the various components of RedisFI, see its help menu for more info.
```
poetry install
poetry run redisfi
```

To run locally, you need a Redis Instance.  Default is `localhost:6379`.  See `--help` to see how to set other than default.

There are two components, a bridge and a webserver.  The bridge integrates all the external data and loads it into Redis.  You can start it with `poetry run redisfi bridge up ALPACA_API_KEY ALPACA_SECRET`, which will load all the various data in the correct order and start the live price adapter. Once it's done, you can start the webserver by running `poetry run redisfi web server`.  Add `--mock` to the bridge and `--debug` to the webserver to enable more of a developer mode.
