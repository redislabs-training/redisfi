from subprocess import Popen

from clikit.api.io.flags import  DEBUG
from cleo import Command, Application

class RunCommand(Command):
    '''
    Use docker compose to run RedisFI

    up
        {--b|build : Build containers from local source}
        {--d|detach : Run in Detached Mode}
        {--redis-host=redis : Location of Redis Server to Use - Defaults to Pulling Container Locally}
        {--redis-port=6379 : Port of Redis Server to Use}
    '''

    def handle(self):

        ## TODO: before we release, invert this logic so that the default includes
        ## a redis instance, and including a --redis-url will not
        
        cmd = ['docker', 'compose']
        up_cmd = ['up']
        profiles = []

        if self.option('build'):
            profiles.append('build')
            up_cmd.append('--build')
        else:
            profiles.append('pull')

        redis_host = self.option('redis-host')
        
        if redis_host == 'redis':
            profiles.append('pull_redis')
        else:
            with open('.env.custom', 'w') as f:
                f.write(f'REDIS_HOST={redis_host}\n')
                f.write(f'REDIS_PORT={self.option("redis-port")}\n')
                cmd.extend(['--env-file', '.env.custom'])

        
        for profile in profiles:
            cmd.extend(['--profile', profile])

        if self.option('detach'):
            up_cmd.append('-d')

        cmd.extend(up_cmd)

        self.line(str(cmd), verbosity=DEBUG)

        with Popen(cmd) as p:
            p.communicate()

def run():
    app = Application(name='redisfi-compose')
    app.add(RunCommand())
    app.run()
