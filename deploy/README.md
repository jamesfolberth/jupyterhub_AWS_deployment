**[Jupyterhub Instances](#jupyterhub-instance)** |
**[Docker Containers](#jupyter-notebook-server-docker-containers)** |
**[Notebook Worker Instances](#jupyter-notebook-worker-instances)** |
**[NFS Instances](#nfs-instance)**

# Configuration of Jupyterhub on AWS
This is our configuration of Jupyterhub, Docker containers for Jupyter notebook instances, and NFS mounted home partitions for the [Northrop Grumman STEM Camp](https://conferencereg.colostate.edu/Registration/Welcome.aspx?e=EB64C01EC8135319E6CDA22A5B404146) - Data Science Track.
We'll have, say, 25 students who will use Jupyter notebooks in a week-long Introductiont to Data Science Summer camp.
The plan is to have Jupyterhub start single-user Jupyter notebooks, which are spawned in Docker containers.
We'll have Docker Swarm start up the containers on one of a few worker nodes.
For data sharing and persistence, we'll mount the user's home directories as an NFS partition, and point the home directory in the Docker containers to the NFS mount.

We started by following the instructions from [Deploying Jupyterhub on AWS](https://github.com/jupyterhub/jupyterhub/wiki/Deploying-JupyterHub-on-AWS).
Another good guide is written up [here](https://zonca.github.io/2016/05/jupyterhub-docker-swarm.html), which uses legacy Docker swarm.
We deviate from each in a few ways, however, so we're writing up our own instructions (in addition James learning about all this stuff!).

1. [Jupyterhub](jupyterhub/README.md)
2. [Webserver Stuff](nginx/README.md)
3. [Docker Swarm Manager and Workers](swarm_legacy/README.md)
4. [NFS](nfs/README.md) (TODO)



## NFS Instance
TODO


## Weird Stuff
I had a weird instance where a worker node dropped out of the swarm (all processes still running).
Maybe it lost the heartbeat?
I did a `docker restart {swarm_worker_container}`, but this got the jupyter container in a redirect loop.
I killed it with docker; can we do it form the admin panel of JHub?


If things get weird, may need to delete the hub's database?
* If a notebook server container failed to start, it may not clear the name `jupyter-{username}`.  We can nuke the DB to "fix" this, but it might cause other issues.  Hmmm... better yet go to the admin control panel and "stop all" (the hub has forgotten that the container is still running)?
