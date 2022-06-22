from subprocess import Popen

from clikit.api.io.flags import  DEBUG
from cleo import Command, Application
from redisfi.tool.commands import ToolBase

class ComposeCommandsBase(Command):
    def handle(self):
        self._handle(**self._configure())

    def _configure(self):
        config = {'cmd': ['docker-compose'],
                  'up_cmd':['up'],
                  'profiles':[],
                  'env':[]}
        
        if self.option('mock'):
            config['env'].append('MOCK=1\n')

        alpaca_key = self.argument('alpaca-api-key')
        alpaca_secret = self.argument('alpaca-api-secret-key')
        
        config['env'].append(f'ALPACA_KEY={alpaca_key}\n')
        config['env'].append(f'ALPACA_SECRET={alpaca_secret}\n')
        
        return config

    def _handle(self, redis_url:str, vss_redis_url:str, cmd:list, up_cmd:list, profiles:list, env:list, **_):
        env.append(f'REDIS_URL={redis_url}\n')
        env.append(f'VSS_REDIS_URL={vss_redis_url}\n')
        
        if 'redis://redis:6379' in (redis_url, vss_redis_url):
            profiles.append('pull_redis')
        
        for profile in profiles:
            cmd.extend(['--profile', profile])

        with open('.env', 'w') as f:
            f.writelines(env)

        cmd.extend(up_cmd)

        self.line(str(cmd), verbosity=DEBUG)

        with Popen(cmd) as p:
            p.communicate()

class UpCommmand(ComposeCommandsBase):
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

    def _configure(self):
        config = super()._configure()
        config['redis_url'] = self.option('redis-url')
        config['vss_redis_url'] = self.option('vss-redis-url')
        
        config['env'].append(f'VSS_URL={self.option("vss-url")}\n')
        
        if self.option('build'):
            config['profiles'].append('build')
            config['up_cmd'].append('--build')
            if not self.option('skip-vss'):
                config['profiles'].append('vss-build')
        else:
            config['profiles'].append('pull')
            if not self.option('skip-vss'):
                config['profiles'].append('vss-pull')

        if self.option('detach'):
            config['up_cmd'].append('-d')

        return config
            

class DeployCommand(ComposeCommandsBase):
    '''
    Use Docker Compose to run app on a server with SSL, optionally using a prebuilt base image

    deploy
        {alpaca-api-key : API key for Alpaca}
        {alpaca-api-secret-key : API secret key for Alpaca}
        {vss-redis-url : Location of the Redis Server for VSS to use}
        {--mock : Start mock live adapter}
    '''

    def _configure(self):
        config = super()._configure()
        config['redis_url'] = 'redis://redis:6379'
        config['vss_redis_url'] = self.argument('vss-redis-url')

        config['env'].append('VSS_URL=http://vss-wsapi:7777\n')

        config['profiles'].append('deployed')
        config['profiles'].append('vss-pull')
        
        return config

def run():
    app = Application(name='redisfi-compose')
    app.add(UpCommmand())
    app.add(ToolBase())
    app.add(DeployCommand())
    app.run()
