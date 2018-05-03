 # jupyterhub_config.py
c = get_config()

import my_oauthenticator

import os
pjoin = os.path.join

runtime_dir = os.path.join('/srv/jupyterhub')

# put the logfile in /var/log/
c.JupyterHub.extra_log_file = '/var/log/jupyterhub.log'

c.JupyterHub.port = 8000
# Since JHub is sitting behind nginx and the JHub serve and swarm workers are
# in a VPC, we don't use SSL for JHub.

c.JupyterHub.cookie_secret_file = pjoin(runtime_dir, 'cookie_secret')
c.JupyterHub.db_url = pjoin(runtime_dir, 'jupyterhub.sqlite')


# use GoogleOAuthenticator + LocalAuthenticator
c.JupyterHub.authenticator_class = my_oauthenticator.LocalGoogleOAuthenticator

c.GoogleOAuthenticator.client_id = os.environ['OAUTH_CLIENT_ID']
c.GoogleOAuthenticator.client_secret = os.environ['OAUTH_CLIENT_SECRET']
c.GoogleOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']


# create system users that don't exist yet
c.Authenticator.create_system_users = True
c.Authenticator.add_user_cmd =  ['adduser', '--home', '/mnt/nfs/home/{username}']

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
c.JupyterHub.proxy_api_ip = '127.0.0.1'
#ConfigurableHTTPProxy.api_url = '127.0.0.1'


# Zonca + legacy swarm
# Point DockerSpawner to Swarm instead of the local DockerEngine
os.environ["DOCKER_HOST"] = ":4000"

c.JupyterHub.spawner_class = 'dockerspawner.SystemUserSpawner'
c.DockerSpawner.image = 'data8-notebook'
#c.DockerSpawner.image = 'jupyter/minimal-notebook' # useful for testing, if the data8 image is borked

## Remove containers once they are stopped
c.Spawner.remove_containers = True

# For debugging arguments passed to spawned containers
c.Spawner.debug = True

c.DockerSpawner.notebook_dir = '/home'


# The docker instances need access to the Hub, so the default loopback port doesn't work:
from jupyter_client.localinterfaces import public_ips
c.JupyterHub.hub_ip = public_ips()[0]


# The docker instances need access to the Hub, so the default loopback port
# doesn't work. We need to tell the hub to listen on 0.0.0.0 because it's in a
# container, and we'll expose the port properly when the container is run. Then,
# we explicitly tell the spawned containers to connect to the proper IP address.
#c.JupyterHub.proxy_api_ip = '0.0.0.0'
c.DockerSpawner.container_ip = '0.0.0.0'
c.DockerSpawner.use_internal_ip = False

c.DockerSpawner.hub_ip_connect = c.JupyterHub.hub_ip


# Mount all of NFS home, including all of the other user's homedirs Since we
# set users up with a UNIX account on the JHub system, the NFS mount will have
# UID/GID (which get set up appropriately in the container too).  This allows
# the user to rw their own files (based on UID/GID) and ro other's files, in
# the usual UNIX permissions manner.
c.DockerSpawner.volumes = { '/mnt/nfs/home': '/home' }

c.SystemUserSpawner.host_homedir_format_string = '/mnt/nfs/home/{username}'

#TODO JMF 3 May 2018: how to rate limit network IO?
#     Our previous data8 image used
#     --NotebookApp.iopub_data_rate_limit=1000000000
#     in $NOTEBOOK_ARGS, which was passed to the Jupyter server.
c.DockerSpawner.extra_host_config = {'mem_limit': '1g',
                                     'cpus': "1",
                                     }

