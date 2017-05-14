# Legacy Docker Swarm
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

2. Install Docker on a new manager or worker node.
   ```bash
   sudo yum update
   sudo yum install docker git
   sudo vim /etc/sysconfig/docker
      # Add OPTIONS = "...  -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock"
   sudo service docker start
   sudo usermod -aG docker ec2-user
   logout
   ```

   We logout and then back in to propogate the group change.

3. If we're a manager, start with the `start_manager.sh` script.
   ```bash
   cd ~/repos/jupyterhub_AWS_deployment/deploy/docker_swarm
   ./start_manager.sh
   ```

   If we're a worker, start with the `start_worker.sh` script.
   I'm not sure it's strictly necessary, but it's potentially wise/better to ensure the manager is already running.
   ```bash
   cd ~/repos/jupyterhub_AWS_deployment/deploy/docker_swarm
   ./start_worker.sh {LOCAL_IPv4_OF_MANAGER}
   ```

4. Add the `userlist` to this worker:
   ```bash
   sudo mkdir -p /srv/jupyterhub
   sudo chown -R ec2-user:ec2-user /srv/jupyterhub/
   chmod -R 700 /srv/jupyterhub
   ```

   (From somewhere else) Copy over the userlist to this worker:
   ```bash
   scp userlist ec2-user@{WORKER_PUBLIC_IPv4}:/srv/jupyterhub/
   ```

   Add users using the script `add_users`:
   ```bash
   cd ~/repos/jupyterhub_AWS_deployment/deploy
   sudo ./add_users
   ```





This works!  The standalone, legacy swarm is handled well by dockerspawner.*, so we'll use it instead of the relatively new
swarm mode built into the docker engine (at least until swarmspawner.SwarmSpawner is reliable, or DockerSpawner handles the API change).  I think the folks working on
dockerspawner are aware of the change, and are thinking about what to do to fix it.  For now, though, it looks like legacy
`docker run swarm ...` is the best way to go.

A good guide is written up [here](https://zonca.github.io/2016/05/jupyterhub-docker-swarm.html).
We use that as a starting point, but need to make a few modifications.

http://jupyterhub.readthedocs.io/en/latest/getting-started.html#configuring-the-proxy-s-ip-address-and-port
https://docs.docker.com/swarm/overview/

Edit /etc/sysconfig/docker  OPTIONS="..." instead of what @andreazonca has.

We need a few extra ports open (2375, 4000, 8500, and 8888).  8888 is used by the hub API and needs to be open for incoming traffic for


## Docker Swarm


`docker -H :4000 ps -a`

echo "alias swarm='docker -H :4000'" >> ~/.bashrc


We've got scripts.

TODO: which ports do we need open on which machines?

### New Swarm Legacy Worker
```bash
sudo yum update
sudo yum install docker git
sudo vim /etc/sysconfig/docker
   # Add OPTIONS = "...  -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock"
sudo service docker start
sudo usermod -aG docker ec2-user
logout
```

```bash
cd && mkdir repos && cd repos
git clone https://github.com/jamesfolberth/NGC_STEM_camp_AWS.git
cd NGC_STEM_camp_AWS
git checkout swarm
cd swarm_worker
./start_legacy $MANAGER_LOCAL_IPv4
```

Check that it joined the swarm.  On the manager
```bash
docker -H :4000 info
```
It might take a moment for the node to show up (especially if you just started up the manager+consul).


add users (+ home dirs?)
```bash
sudo run_a_script.sh
```

Add docker images
```bash
cd ~/repos/NGC_STEM_camp_AWS/data8-notebook
./build.sh
```

We'll eventually save an AMI, I think.  Then we'll just have to SSH in and join the swarm.
