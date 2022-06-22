from subprocess import Popen

from clikit.api.io.flags import  DEBUG
from cleo import Command, Application
from redisfi.tool.commands import ToolBase

class RunCommand(Command):
    '''
    Use docker compose to run RedisFI

    up
        {alpaca-api-key : API key for Alpaca}
        {alpaca-api-secret-key : API secret key for Alpaca}
        {--b|build : Build containers from local source}
        {--d|detach : Run in Detached Mode}
        {--redis-url=redis://redis:6379 : Location of Redis Server to Use - Defaults to Pulling Container Locally}
        {--vss-redis-url=redis://redis:6379 : Location of the Redis Server for VSS to use - Defaults to Pulling Container Locally}
        {--vss-url=http://vss-wsapi:7777 : Location of VSS microservice}
        {--mock : Start mock live adapter}
        {--skip-vss : Don't include the VSS part of the Demo}
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
        
        if not self.option('skip-vss'):
            if 'pull' in profiles:
                profiles.append('vss-pull')
            else:
                profiles.append('vss-build')
            
        if self.option('mock'):
            env.append('MOCK=1\n')


        alpaca_key = self.argument('alpaca-api-key')
        alpaca_secret = self.argument('alpaca-api-secret-key')
        vss_url = self.option('vss-url')
        redis_url = self.option('redis-url')
        vss_redis_url = self.option('vss-redis-url')
        
        env.append(f'ALPACA_KEY={alpaca_key}\n')
        env.append(f'ALPACA_SECRET={alpaca_secret}\n')
        env.append(f'VSS_URL={vss_url}\n')
        env.append(f'REDIS_URL={redis_url}\n')
        env.append(f'VSS_REDIS_URL={vss_redis_url}\n')

        if 'redis://redis:6379' in (redis_url, vss_redis_url):
            profiles.append('pull_redis')
        
        for profile in profiles:
            cmd.extend(['--profile', profile])

        if self.option('detach'):
            up_cmd.append('-d')

        with open('.env', 'w') as f:
            f.writelines(env)

        cmd.extend(up_cmd)

        self.line(str(cmd), verbosity=DEBUG)

        with Popen(cmd) as p:
            p.communicate()

def run():
    app = Application(name='redisfi-compose')
    app.add(RunCommand())
    app.add(ToolBase())
    app.run()
