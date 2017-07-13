 # jupyterhub_config.py
c = get_config()

import my_oauthenticator

import os
pjoin = os.path.join

runtime_dir = os.path.join('/srv/jupyterhub')
ssl_dir = pjoin(runtime_dir, 'ssl')
if not os.path.exists(ssl_dir):
    os.makedirs(ssl_dir)

c.JupyterHub.port = 8000
c.JupyterHub.ssl_key = pjoin(ssl_dir, 'hub.key')
c.JupyterHub.ssl_cert = pjoin(ssl_dir, 'hub.crt')

c.JupyterHub.cookie_secret_file = pjoin(runtime_dir, 'cookie_secret')
c.JupyterHub.db_url = pjoin(runtime_dir, 'jupyterhub.sqlite')


# use GoogleOAuthenticator + LocalAuthenticator
c.JupyterHub.authenticator_class = my_oauthenticator.LocalGoogleOAuthenticator

c.GoogleOAuthenticator.client_id = os.environ['OAUTH_CLIENT_ID']
c.GoogleOAuthenticator.client_secret = os.environ['OAUTH_CLIENT_SECRET']
c.GoogleOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']


# create system users that don't exist yet
c.Authenticator.create_system_users = True
# Default adduser flags are for FreeBSD (works on CentOS 5, Debian, Ubuntu)
# Doesn't work for us.
# https://github.com/jupyterhub/jupyterhub/issues/696
#c.Authenticator.add_user_cmd =  ['adduser', '--home', '/home/USERNAME']
c.Authenticator.add_user_cmd =  ['adduser', '--home', '/mnt/nfs/home/USERNAME'] # not yet
#TODO JMF 16 May 2017: I've hacked around in my_oauthenticator.py.  Need to make this a bit more robust.

c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()

with open(pjoin(runtime_dir, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        if parts:
            name = parts[0]
            whitelist.add(name)
            if len(parts) > 1 and parts[1] == 'admin':
                admin.add(name)




# nginx config stuff
# Force the proxy to only listen to connections to 127.0.0.1
c.JupyterHub.ip = '127.0.0.1'
#c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.proxy_api_ip = '127.0.0.1'


# Zonca + legacy swarm
# Point DockerSpawner to Swarm instead of the local DockerEngine
os.environ["DOCKER_HOST"] = ":4000"

c.JupyterHub.spawner_class = 'dockerspawner.SystemUserSpawner'
c.DockerSpawner.container_image = 'data8-notebook'

## Remove containers once they are stopped
c.Spawner.remove_containers = True

# For debugging arguments passed to spawned containers
c.Spawner.debug = True



#notebook_dir = '/home/{username}'
#c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.notebook_dir = '/home'


# The docker instances need access to the Hub, so the default loopback port doesn't work:
from jupyter_client.localinterfaces import public_ips
c.JupyterHub.hub_ip = public_ips()[0]
#print('hub_ip = ',c.JupyterHub.hub_ip)


# The docker instances need access to the Hub, so the default loopback port
# doesn't work. We need to tell the hub to listen on 0.0.0.0 because it's in a
# container, and we'll expose the port properly when the container is run. Then,
# we explicitly tell the spawned containers to connect to the proper IP address.
#c.JupyterHub.proxy_api_ip = '0.0.0.0'
c.DockerSpawner.container_ip = '0.0.0.0'
c.DockerSpawner.use_internal_ip = False

c.DockerSpawner.hub_ip_connect = c.JupyterHub.hub_ip




# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container.  Mount all of NFS home
c.DockerSpawner.volumes = { '/mnt/nfs/home': '/home' }

c.SystemUserSpawner.host_homedir_format_string = '/mnt/nfs/home/{username}'

#c.DockerSpawner.extra_host_config = {'mem_limit': '1g'}
#c.DockerSpawner.extra_host_config = {'mem_limit': '50m'}

