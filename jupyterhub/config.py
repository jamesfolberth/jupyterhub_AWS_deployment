 # jupyterhub_config.py
c = get_config()

import my_oauthenticator

import os
pjoin = os.path.join

runtime_dir = os.path.join('/srv/jupyterhub')
ssl_dir = pjoin(runtime_dir, 'ssl')
if not os.path.exists(ssl_dir):
    os.makedirs(ssl_dir)

# https on :8443
#TODO not on 8443, use nginx to handle 443
c.JupyterHub.port = 8443
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
c.Authenticator.add_user_cmd =  ['adduser', '--home', '/mnt/nfs/home/USERNAME']

c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()

with open(pjoint(runtime_dir, 'userlist') as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        name = parts[0]
        whitelist.add(name)
        if len(parts) > 1 and parts[1] == 'admin':
            admin.add(name)


# start single-user notebook servers in ~/assignments,
# with ~/assignments/Welcome.ipynb as the default landing page
# this config could also be put in
# /etc/jupyter/jupyter_notebook_config.py
#c.Spawner.notebook_dir = '~/notebooks'
#c.Spawner.args = ['--NotebookApp.default_url=/notebooks/lab01.ipynb']

# Spawn user containers from this image
c.DockerSpawner.container_image = 'jupyter_node'
#c.DockerSpawner.container_image = 'systemuser'

# Have the Spawner override the Docker run command
#c.DockerSpawner.extra_create_kwargs.update({
#	'command': '/usr/local/bin/start-singleuser.sh'
#	#'command': '/usr/local/bin/start-systemuser.sh'
#})

#TODO get rid of user jovyan; see systemuserspawner
#notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
#notebook_dir = '/home/{username}'
#c.DockerSpawner.notebook_dir = notebook_dir
#c.DockerSpawner.notebook_dir = '/'
#c.DockerSpawner.notebook_dir = notebook_dir
#c.DockerSpawner.default_url = '/home/{username}' #TODO doesn't work


#TODO we eventually want systemuserspawner, I think
#c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.JupyterHub.spawner_class = 'dockerspawner.SystemUserSpawner'

# The docker instances need access to the Hub, so the default loopback port doesn't work:
from jupyter_client.localinterfaces import public_ips
c.JupyterHub.hub_ip = public_ips()[0]


c.SystemUserSpawner.host_homedir_format_string = '/mnt/nfs/home/{username}'


#TODO data persistence and NFS
# Explicitly set notebook directory because we'll be mounting a host volume to
# it.  Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
#notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
#c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
#c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
#c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
#c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })


# Remove containers once they are stopped
c.Spawner.remove_containers = True

# For debugging arguments passed to spawned containers
c.Spawner.debug = True


