# jupyterhub/systemuser

Built from the `jupyter/scipy-notebook` base image.

This image contains a single user notebook server for use with
[JupyterHub](https://github.com/jupyterhub/jupyterhub). In particular, it is meant
to be used with the
[SystemUserSpawner](https://github.com/jupyterhub/dockerspawner/blob/master/dockerspawner/systemuserspawner.py)
class to launch user notebook servers within docker containers.

This particular server initially runs (within the container) as the `root` user.
When the container is run, it expects to have access to environment variables
for `$USER`, `$USER_ID`, and `$HOME`. It will create a user inside the container
with the specified username and id, and then run the notebook server as that
user (using `sudo`). It also expects the user's home directory (specified by
`$HOME`) to exist -- for example, by being mounted as a volume in the container
when it is run.

## Building
Due to the size of things we download and upload, I like to build on AWS.
You'll want to use a somewhat beefy instance (e.g., >= t2.large with 32 GB of space on the root partition).


```bash
./get_extra_data.sh
# edit Dockerfile
./build.sh
```

To push to hub.docker.com, you'll need to first create a DockerHub account and configure the local docker daemon to use the approprate creditials.
Note that the docker daeomon will ask for your hub.docker.com username and password, but it looks like it doesn't store your info in `~/.docker/config.json`.
Nevertheless, be prudent.

Next, you'll tag the image you want to push, and then push that tagged image.
For example,

```bash
docker login
docker tag {THE_IMAGE_YOU_WANT} jamesfolberth/data8-notebook
docker push jamesfolberth/data8-notebook
```

See [docker push](https://docs.docker.com/engine/reference/commandline/push/#extended-description) for more info.

