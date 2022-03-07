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
        {--mock : Start mock live adapter}
    '''

    def handle(self):

        cmd = ['docker-compose']
        up_cmd = ['up']
        profiles = []
        env = []

        if self.option('build'):
            profiles.append('build')
            up_cmd.append('--build')
        else:
            profiles.append('pull')
        
        if self.option('mock'):
            env.append('MOCK=1')

        redis_host = self.option('redis-host')
        
        if redis_host == 'redis':
            profiles.append('pull_redis')
        else:
            env.append(f'REDIS_HOST={redis_host}')
            env.append(f'REDIS_PORT={self.option("redis-port")}')
        
        for profile in profiles:
            cmd.extend(['--profile', profile])

        if self.option('detach'):
            up_cmd.append('-d')

        if env:
            with open('.env.custom', 'w') as f:
                f.writelines(env)
            
            cmd.extend(['--env-file', '.env.custom'])


        cmd.extend(up_cmd)

        self.line(str(cmd), verbosity=DEBUG)

        with Popen(cmd) as p:
            p.communicate()

def run():
    app = Application(name='redisfi-compose')
    app.add(RunCommand())
    app.run()
