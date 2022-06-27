from subprocess import run as _run_cmd, Popen
from base64 import b64decode

from clikit.api.io.flags import  DEBUG
from cleo import Command, Application
from redisfi.tool.commands import ToolBase

run_cmd = lambda cmd: _run_cmd(cmd, shell=True)

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
    Use Docker Compose to run app on a server with SSL, requires using a prebuilt base image.

    deploy
        {domain : Domain Name that we're Running As}
        {alpaca-api-key : API key for Alpaca}
        {alpaca-api-secret-key : API secret key for Alpaca}
        {vss-redis-url : Location of the Redis Server for VSS to use}
        {base-container-url : (GCP Based) Location of container built using ssl.dockerfile + app.dockerfile}
        {encoded-credentials : Base64 encoded (GCP) creds for above container}
        {--mock : Start mock live adapter}
    '''
    ## this function is rather bespoke for redis [the company] internal needs - it could be more generic if needed

    def handle(self):
        self._config = self._configure()
        self._authorize_and_pull_base_container()
        self._handle(**self._config)

    def _authorize_and_pull_base_container(self):
        with open('auth.json', 'w') as f:
            f.write(self._config['container_auth_json'])

        run_cmd(f"gcloud auth activate-service-account --key-file auth.json")
        run_cmd('gcloud auth configure-docker')
        run_cmd(f'docker pull {self._config["base_container_url"]}')
        run_cmd(f'docker logout {self._config["base_container_url"]}')
        run_cmd(f'rm auth.json')

    def _configure(self):
        config = super()._configure()
        config['redis_url'] = 'redis://redis:6379'
        config['vss_redis_url'] = self.argument('vss-redis-url')
        config['base_container_url'] = self.argument('base-container-url')
        config['container_auth_json'] = b64decode(self.argument('encoded-credentials')).decode('ascii')
        
        domain = self.argument('domain')
        cert_name = '.'.join(domain.split('.')[1:])

        config['env'].append('VSS_URL=http://vss-wsapi:7777\n')
        config['env'].append(f'BASE={config["base_container_url"]}\n')
        config['env'].append(f'DOMAIN={domain}\n')
        config['env'].append(f'CERT_NAME={cert_name}\n')

        config['profiles'].append('deployed-prebuilt')
        config['profiles'].append('vss-pull')
        
        return config

def run():
    app = Application(name='redisfi-compose')
    app.add(UpCommmand())
    app.add(ToolBase())
    app.add(DeployCommand())
    app.run()
