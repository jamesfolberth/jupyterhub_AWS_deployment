# Legacy Docker Swarm
## Setup
We follow [Andrea Zonca's guide](https://zonca.github.io/2016/05/jupyterhub-docker-swarm.html) for setting up JHub and [DockerSpawner](https://github.com/jupyterhub/dockerspawner) to spawn notebook server containers in a <i>legacy</i> Docker swarm.
At the time of this writing, there aren't yet good ways to handling the new swarm mode that's integrated into the Docker engine.
This is probably going to be fixed in the future, but for now, it should provide a (stable) way to use Docker swarm.
Documentation for <i>legacy</i> Docker swarm can be found [here](https://docs.docker.com/swarm/overview/).

1. We'll need a few ports open:
   We create another security group named "Swarm Manager" that has the following ports open to the VPC.
   Again, I think we can just open them all up to the VPC.
   Ports 2375, 4000, and 8500 are used by Docker swarm and consul, a distributed key-store used to store information about the nodes.
   Ports 32000-33000 are used by the Jupyter notebook servers (inside of Docker containers).

      |Ports |	Protocol	| Source |
      |------|----------|--------|
      |2375	| tcp	| 172.31.0.0/16 |
      |4000	| tcp	| 172.31.0.0/16 |
      |8500| tcp	| 172.31.0.0/16 |
      |32000-33000| tcp	| 172.31.0.0/16 |

   We make a final security group named "Swarm Worker" that has the following ports open to the VPC.

      |Ports |	Protocol	| Source |
      |------|----------|--------|
      |2375	| tcp	| 172.31.0.0/16 |
      |4000	| tcp	| 172.31.0.0/16 |
      |8500| tcp	| 172.31.0.0/16 |

     Alternatively, we can just open up port 22 to the outside world and all ports inside the VPC (172.31.0.0/16).

2. Install Docker on a new manager or worker node.
   ```bash
   sudo yum -y update
   curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | sudo bash
   sudo yum -y install docker git git-lfs
   sudo vim /etc/sysconfig/docker
      # Add OPTIONS = "...  -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock"
   sudo service docker start
   sudo usermod -aG docker ec2-user
   logout
   ```

   Logout and then log back in to propagate the group change.

3. Do the [NFS stuff](../nfs/README.md).

4. Clone this repo:
   ```bash
   cd && mkdir repos && cd repos
   git clone https://github.com/jamesfolberth/jupyterhub_AWS_deployment.git
   ```

   Build the notebook image
   ```bash
   cd ~/repos/jupyterhub_AWS_deployment/deploy/data8-notebook
   ./build.sh
   ```

   Alternatively, you can pull the latest version of data8-notebook from Docker hub.
   ```bash
   cd ~/repos/jupyterhub_AWS_deployment/deploy/data8-notebook
   ./pull.sh
   ```
   This will pull jamesfolberth/data8-notebook:latest and tag it as data8-notebook.


   If we're a manager, start with the `start_manager.sh` script.
   ```bash
   cd ~/repos/jupyterhub_AWS_deployment/deploy/swarm_legacy
   ./start_manager.sh
   ```

   If we're a worker, start with the `start_worker.sh` script.
   I'm not sure it's strictly necessary, but it's potentially wise/better to ensure the manager is already running.
   ```bash
   cd ~/repos/jupyterhub_AWS_deployment/deploy/swarm_legacy
   ./start_worker.sh {LOCAL_IPv4_OF_MANAGER}
   ```

   You can get the local IP of the manager instance by running `ec2-metadata` on the manager node or looking in the AWS console.

5.  This should get everything set up.

## Some Helpful Commands
Here are some useful docker commands

```
# What's running on the local machine?
docker ps -a

# What's running in the swarm?  (run on the manager)
docker -H :4000 ps -a

# Information about the state of the swarm?  (run on the manager)
docker -H :4000 info
```

If you want to shut down a worker instance, I'd follow these steps:
* Run `docker -H :4000 ps -a` on the manager node to see which containers are running on the worker you want to shut down.
* From the Jupyterhub Admin page, shut down those containers (or ask the users to shut them down and log out of their single-user notebook servers).
* Stop the swarm image on the worker, which will let the worker leave.
  Note that it may take a minute or two for `docker -H :4000 info` to reflect the lost worker.
* It should be safe to shut down the worker.
