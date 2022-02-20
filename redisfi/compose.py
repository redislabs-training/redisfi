from subprocess import Popen

from clikit.api.io.flags import VERBOSE
from cleo import Command
from redis import Redis
from redis.exceptions import ConnectionError

class RunCommand(Command):
    '''
    Use docker compose to run RedisFI

    run
        {--redis-url=redis://localhost:6379 : Location of the redis server to use}
        {--include-redis : Add a Redis Container to Docker Compose}
    '''

    def handle(self):

        ## TODO: before we release, invert this logic so that the default includes
        ## a redis instance, and including a --redis-url will not
        
        redis_url = self.option('redis-url')
        self.line(f'redis url: {redis_url}', verbosity=VERBOSE)
        test_redis = Redis.from_url(redis_url)
        try:
            test_redis.ping()
        except ConnectionError:
            self.line_error('Invalid Redis URL')

        if self.option('include-redis'):
            print('include redis')
        else:
            with Popen(['docker', 'compose', 'up']) as p:
                p.communicate()


