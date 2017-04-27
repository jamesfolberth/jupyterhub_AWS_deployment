 # jupyterhub_config.py
c = get_config()

import my_oauthenticator
import dummyauthenticator
import docker_oauth

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
#c.JupyterHub.authenticator_class = my_oauthenticator.LocalGoogleOAuthenticator
#XXX: For testing only
c.JupyterHub.authenticator_class = dummyauthenticator.DummyAuthenticator
#c.JupyterHub.authenticator_class = docker_oauth.DockerDummy

c.GoogleOAuthenticator.client_id = os.environ['OAUTH_CLIENT_ID']
c.GoogleOAuthenticator.client_secret = os.environ['OAUTH_CLIENT_SECRET']
c.GoogleOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

# create system users that don't exist yet
c.Authenticator.create_system_users = True
# Default adduser flags are for FreeBSD (works on CentOS 5, Debian, Ubuntu)
# Doesn't work for us.
# https://github.com/jupyterhub/jupyterhub/issues/696
#c.Authenticator.add_user_cmd =  ['adduser', '--disabled-password', '--quiet',
#    '--gecos', '""', '--home', '/home/USERNAME', '--force-badname']

#c.Authenticator.add_user_cmd =  ['adduser', '--home', '/mnt/nfs/home/USERNAME'] # not yet

c.Authenticator.whitelist = ['james', 'testuser']
#c.Authenticator.whitelist = whitelist = set()
#c.Authenticator.admin_users = admin = set()
#
#with open(pjoin(runtime_dir, 'userlist')) as f:
#    for line in f:
#        if not line:
#            continue
#        parts = line.split()
#        name = parts[0]
#        whitelist.add(name)
#        if len(parts) > 1 and parts[1] == 'admin':
#            admin.add(name)



# Try using SwarmSpawner from https://github.com/cassinyio/SwarmSpawner.git
c.JupyterHub.spawner_class = 'cassinyspawner.SwarmSpawner'


c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.proxy_api_ip = '0.0.0.0'
#c.JupyterHub.hub_ip = 'jupyterhub_service'
# The docker instances need access to the Hub, so the default loopback port doesn't work:
#from jupyter_client.localinterfaces import public_ips
#c.JupyterHub.hub_ip = public_ips()[0]


c.JupyterHub.cleanup_servers = True #TODO temp

# First pulls can be really slow, so let's give it a big timeout
c.SwarmSpawner.start_timeout = 60 * 5
#c.SwarmSpawner.start_timeout = 15

c.SwarmSpawner.jupyterhub_service_name = 'jupyterhub_service'

c.SwarmSpawner.networks = ["hubnet"]

#notebook_dir = os.environ.get('NOTEBOOK_DIR') or '/home/jovyan/work'
notebook_dir = '/home/{username}'
#notebook_dir = '/home/jovyan/work'
c.SwarmSpawner.notebook_dir = notebook_dir # TODO
#c.SwarmSpawner.notebook_dir = '/'

mounts = []
#mounts.append({'type' : 'volume',
#               'source' : 'jupyterhub-user-{username}',
#               'target' : notebook_dir})
mounts.append({'type': 'bind',
               'source': '/home/{username}',
               'target': notebook_dir})
#mounts = [{'type': 'bind',
#          'source': '/home/jamesfolberth',
#          'target': '/home/jamesfolberth'}]


c.SwarmSpawner.container_spec = {
    # The command to run inside the service
    #'args' : ['/usr/local/bin/start-systemuser.sh'], #list
    #'args': ['sh', '/usr/local/bin/start-systemuser.sh'] ,
    'Image' : 'data8-notebook',
    #'Image' : 'jupyter/minimal-notebook',
    'mounts' : mounts
    #'mounts' : []
    }

c.SwarmSpawner.debug = True

#c.SwarmSpawner.resource_spec = {
#                'cpu_limit' : 1000, # (int) – CPU limit in units of 10^9 CPU shares.
#                'mem_limit' : int(512 * 1e6), # (int) – Memory limit in Bytes.
#                'cpu_reservation' : 1000, # (int) – CPU reservation in units of 10^9 CPU shares.
#                'mem_reservation' : int(512 * 1e6), # (int) – Memory reservation in Bytes
#                }





## start single-user notebook servers in ~/assignments,
## with ~/assignments/Welcome.ipynb as the default landing page
## this config could also be put in
## /etc/jupyter/jupyter_notebook_config.py
##c.Spawner.notebook_dir = '~/notebooks'
##c.Spawner.args = ['--NotebookApp.default_url=/notebooks/lab01.ipynb']
#
## Spawn user containers from this image
#c.DockerSpawner.container_image = 'data8-notebook'
##c.DockerSpawner.container_image = 'systemuser'
#
## Have the Spawner override the Docker run command
##c.DockerSpawner.extra_create_kwargs.update({
##	'command': '/usr/local/bin/start-singleuser.sh'
##	#'command': '/usr/local/bin/start-systemuser.sh'
##})
#
##TODO get rid of user jovyan; see systemuserspawner
##notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
##notebook_dir = '/home/{username}'
##c.DockerSpawner.notebook_dir = notebook_dir
##c.DockerSpawner.notebook_dir = '/'
##c.DockerSpawner.notebook_dir = notebook_dir
##c.DockerSpawner.default_url = '/home/{username}' #TODO doesn't work
#
#
##TODO we eventually want systemuserspawner, I think
##c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
#c.JupyterHub.spawner_class = 'dockerspawner.SystemUserSpawner'
#
#c.DockerSpawner.use_docker_client_env = True
#
## The docker instances need access to the Hub, so the default loopback port doesn't work:
#from jupyter_client.localinterfaces import public_ips
#c.JupyterHub.hub_ip = public_ips()[0]
#
#
#c.SystemUserSpawner.host_homedir_format_string = '/mnt/nfs/home/{username}' # not yet
##c.SystemUserSpawner.host_homedir_format_string = '/home/{username}'
#
#
## Use `docker port` to determine where to start container
##c.SystemUserSpawner.container_ip = '172.31.47.221:2377'
#c.SystemUserSpawner.container_ip = '0.0.0.0'
#c.DockerSpawner.network_name = 'hubnet'
#
#
## From https://gist.github.com/zonca/83d222df8d0b9eaebd02b83faa676753
## The docker instances need access to the Hub, so the default loopback port
## doesn't work. We need to tell the hub to listen on 0.0.0.0 because it's in a
## container, and we'll expose the port properly when the container is run. Then,
## we explicitly tell the spawned containers to connect to the proper IP address.
##os.environ["DOCKER_HOST"] = ":2377"
##c.JupyterHub.proxy_api_ip = '0.0.0.0'
##c.DockerSpawner.container_ip = '0.0.0.0'
##c.DockerSpawner.use_internal_ip = False
##
##c.DockerSpawner.hub_ip_connect = c.JupyterHub.hub_ip
#
#
#
## From https://github.com/smashwilson/jupyterhub-on-docker-swarm/blob/gh-pages/jupyterhub-launch/jupyterhub_config.py
##c.JupyterHub.hub_ip = "0.0.0.0"
##c.SystemUserSpawner.tls_verify = True
##c.SystemUserSpawner.use_internal_ip = True
##c.SystemUserSpawner.hub_ip_connect = os.environ["EC2_PUBLIC_HOSTNAME"]
#
#
##TODO data persistence and NFS
## Explicitly set notebook directory because we'll be mounting a host volume to
## it.  Most jupyter/docker-stacks *-notebook images run the Notebook server as
## user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
## We follow the same convention.
##notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
##c.DockerSpawner.notebook_dir = notebook_dir
#
## Mount the real user's Docker volume on the host to the notebook user's
## notebook directory in the container
##c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
#
## Mount the real user's Docker volume on the host to the notebook user's
## notebook directory in the container
##c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
##c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })
#
#
## Remove containers once they are stopped
#c.Spawner.remove_containers = True
#
## For debugging arguments passed to spawned containers
#c.Spawner.debug = True


