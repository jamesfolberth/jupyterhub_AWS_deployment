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

## Jupyterhub Instance
We followed most of the instructions from [Deploying Jupyterhub on AWS](https://github.com/jupyterhub/jupyterhub/wiki/Deploying-JupyterHub-on-AWS).
We deviate in a few ways, however, since we have not registered a domain name.

1. Starting the hub VM
   * We developed and tested the config files on a t2.micro instance.
     For deployment, we'll probably want a larger instance for the hub, especially if it will also run a few notebook containers.
     We used a standard 64-bit Amazon Linux AMI.
     It has a reasonable number of packages in the `yum` repo, and most of the rest of the software we use can be installed with `pip`.
     We set the following inbound rules:

    |Ports |	Protocol	| Source |
    |------|----------|--------|
    |22	| tcp	| 0.0.0.0/0, ::/0 |
    |443	| tcp	| 0.0.0.0/0, ::/0 |
    |8443	| tcp	| 0.0.0.0/0, ::/0 |

   * We may eventually put nginx in front to host a (probably very simple) website and Jupyterhub, both on 443.

2. Install a bunch of packages
   * To connect to the new instance, you'll need your SSH key (if it's your first time, you'll need AWS to generate one for you).
     Once you've downloaded your AWS SSH key and started up your instance, you can connect to it with `ssh -i ~/.ssh/aws_key.pem ec2-user@{PUBLIC_IPv4ADDR}`.
      The standard user is `ec2-user`, which has `sudo` privileges; once inside, you can make new users if you prefer.
      We'll use `ec2-user2` to orchestrate everything.

   * Make a directory for Jupyterhub server files (e.g., SSL certs, user list)
      ```bash
      sudo mkdir -p /srv/jupyterhub
      sudo chown -R ec2-user:ec2-user /srv/jupyterhub/
      chmod -R 700 /srv/jupyterhub
      ```

   * Install a bunch of packages from the system repos.
      ```bash
      sudo yum update
      sudo yum install python34 python34-pip python34-devel git docker gcc gcc-c++
      sudo service docker start
      ```

   * Add `ec2-user` to the Docker group, so we don't have to `sudo` every time we want to run a Docker container.
      This is useful for testing things out.
      ```bash
      sudo usermod -aG docker ec2-user
      ```

   * Logout and back in to make group changes for `ec2-user`.  Verify changes with `groups`.

   * Verify docker works with `docker run hello-world`.

   * Download Node.js and npm.  You may want to visit [nodejs.org](https://nodejs.org/en/download/) to get a different version.
     ```bash
     cd && mkdir downloads && cd downloads

     wget https://nodejs.org/dist/v6.10.2/node-v6.10.2-linux-x64.tar.xz
     tar -xvf node-v6.10.2-linux-x64.tar.xz
     cd node-v6.10.2-linux-x64
     sudo cp -r bin/* /usr/bin/
     sudo cp -r include/* /usr/include/
     sudo cp -r lib/* /usr/lib/
     sudo cp -r share/* /usr/share/
     cd ..

     wget https://npmjs.org/install.sh
     chmod +x install.sh
     sudo ./install.sh
     cd ..
     ```

   * Install [configurable-http-proxy](https://github.com/jupyterhub/configurable-http-proxy).
     ```bash
     sudo npm install -g configurable-http-proxy
     ```

   * Install python packages with `pip`.
     ```bash
     sudo pip-3.4 install jupyterhub
     sudo pip-3.4 install --upgrade notebook
     sudo pip-3.4 install oauthenticator dockerspawner
     ```

3. Generate a self-signed SSL certificate.
   * We don't have a domain name for our project, so we'll use a self-signed SSL certificate for now.
     Also, a self-signed cert is quite okay for testing/development.
     ```bash
     sudo mkdir /srv/jupyterhub/ssl
     sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /srv/jupyterhub/ssl/hub.key -out /srv/jupyterhub/ssl/hub.crt
     ```
     
3. Set up nginx and SSL
   * hub subdomain
   http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingNewSubdomain.html
   https://aws.amazon.com/premiumsupport/knowledge-center/create-subdomain-route-53/
   
   * Install nginx
    ```bash
    sudo yum install nginx
    sudo service nginx start
    ```

    You can test the nginx install by pointing your web browswer to the IP of the EC2 instance.
    You should see a default `index.html`.

    http://jupyterhub.readthedocs.io/en/latest/config-examples.html
    https://www.nginx.com/blog/setting-up-nginx/

   * Generate an SSL key with Let's Encrypt
    ```bash
    cd && mkdir repos && cd repos
    git clone https://github.com/letsencrypt/letsencrypt
    cd letsencrypt
    ./letsencrypt-auto certonly --standalone -v -d 
    ```
    TODO: for now we use our self-signed cert
    
    https://aws.amazon.com/premiumsupport/knowledge-center/ec2-enable-epel/
    ```bash
    sudo yum-config-manager --enable epel
    ```
    
    ```bash
    cd downloads
    wget https://dl.eff.org/certbot-auto
    chmod a+x certbot-auto
    ./certbot-auto certonly --standalone -d jamesfolberth.org --debug # need debug on Amazon Linux
    ```
    
    Editing nginx  config files
    
    ```bash
    openssl dhparam -out /etc/letsencrypt/live/jamesfolberth.org/
    
   * nginx config
   ```bash
   sudo su
   cd /etc/nginx/
   mv nginx.conf nginx.conf.bak
   ```
   Now edit `/etc/nginx/nginx.conf`:
   ```
    # For more information on configuration, see:
#   * Official English Documentation: http://nginx.org/en/docs/
#   * Official Russian Documentation: http://nginx.org/ru/docs/

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /var/run/nginx.pid;

# Load dynamic modules. See /usr/share/nginx/README.dynamic.
include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}
   ```
   
   ```bash
   cd conf.d
   ```
   Redirect HTTP->HTTPS on a per-server basis
   https://www.bjornjohansen.no/redirect-to-https-with-nginx

4. Register the project with Google OAuth 2.0
   * Note that each time we spin up a new AMI, it will (almost surely) get a new IP address.  We can buy an elastic IP, but for the purposes of development, we'll just have to update the IP and URIs below each time we spin up a new hub instance.

   * We want to use Google's authentication system for our project.  A lot of Jupyterhub deployments use GitHub authentication, which is good for their use-case, but for us, Google is probably simpler.
     Specificaly, we want to create an OAuth 2.0 Client ID for our project, so the users can authenticate with their Google accounts.
     Go to [Google API Manager](https://console.developers.google.com/apis/credentials) to set up a project.
     You'll need to set a meaningful project name, and get the domain name of your AWS hub instance (might be something like https://ec2-{IPv4ADDR}.us-west-2.compute.amazonaws.com).
     We'll be using port 8443 for the hub, as we may eventually use nginx as a port 443 front-end.

     Then set the authorized JS origins and callback URI:
     ```
     Authorized JavaScript origins:
         https://ec2-{IPv4ADDR}.us-west-2.compute.amazonaws.com:8443
     Authorized callback URIs:
         https://ec2-{IPv4ADDR}.us-west-2.compute.amazonaws.com:8443/hub/oauth_callback
     ```

   * Once you've created the project, copy the client ID and secret to the file `/srv/jupyterhub/env`.
    ```bash
    # Google OAuth 2.0
    export OAUTH_CLIENT_ID=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA.apps.googleusercontent.com
    export OAUTH_CLIENT_SECRET=BBBBBBBBBBBBBBBBBBBBB
    ```
    Do note that these are secret, and should not be pushed to a git repo or accessible for other users (hence the chmod 700 in the beginning).

5. Set up Jupyterhub
   * Add users to `/srv/jupyterhub/userlist` with the following format
     ```
     user.name@gmail.com
     admin.user@gmail.com admin
     anotheruser@gmail.com
     ```
     
     TODO: need to make a script to add users to the system.  Should be run on all machines too (i.e., take in userlist as an argument)
     
     As currently configured, Jupyterhub will create system users with the names `user.name`, `admin.user`, etc., and appropriate home directories.  `admin.user` won't have any special permissions on the underlying host system, but will be able to manage user notebook servers from Jupyterhub.

   * Clone this repo on the Jupyterhub host. ### and copy contents to a deploy folder.
   ```bash
   cd && mkdir repos && cd repos
   git clone https://github.com/jamesfolberth/NGC_STEM_camp_AWS.git
   cd NGC_STEM_camp_AWS/jupyterhub
   ```
   

   * Optionally NAT port 443 to 8443 to be served by the hub.  We may put nginx on the front end to route to both the hub and a (simple) webserver.
     ```bash
     sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to 8443
     ```

   * We haven't yet built Docker containers for the notebook instances, but we can still test out the hub a bit.  Start up the hub with `./start.sh`, which will set up a few environment variables and then run `sudo jupyterhub`.  The script uses `ec2-metadata` to get the running instance's public hostname.

     Point your browser to `https://{PUBLIC_IPv4ADDR}:8443`.  You should see a warning that the connection is untrusted (because we're using a self-signed SSL cert), but you can proceed.  You should see a Google authentication page, which, once authenticated, will pass you to the main Jupyterhub page, where you can start a server, view the control panel, etc.

     Since we haven't built the notebook server Docker containers, clicking "Start My Server" should error out (500).  If we didn't authenticate properly (perhaps the email in `/srv/jupyterhub/userlist` is misspelled), you'll see an error 403.


## Jupyter Notebook Server Docker Container
We've combined what we like from a few Jupyter notebook docker containers, and merged them into one.  We've used code from Jupyter's [minimal-notebook](https://github.com/jupyter/docker-stacks/tree/master/minimal-notebook), [scipy-notebook](https://github.com/jupyter/docker-stacks/tree/master/scipy-notebook), and from Jupyterhub's [systemuser](https://github.com/jupyterhub/dockerspawner/tree/master/systemuser).

In the `data8-notebook` directory, there is a `Dockerfile`, and a few helper files.  We use Jupyter's [minimal-notebook](https://github.com/jupyter/docker-stacks/tree/master/minimal-notebook) as a base, then install [Anaconda](https://www.continuum.io/downloads) Python 3 and a variety of conda packages.  There are a few other little tweaks included from [scipy-notebook](https://github.com/jupyter/docker-stacks/tree/master/scipy-notebook).  Finally, we run the Jupyterhub single user notebook server a la [systemuser](https://github.com/jupyterhub/dockerspawner/tree/master/systemuser).

To build the image,
```bash
cd data8-notebook && ./build.sh
```
This will build the Docker image and give it the tag `data8-notebook`.  The Jupyterhub config `jupyterhub/confg.py` will use SystemUserSpawner from [dockerspawner](https://github.com/jupyterhub/dockerspawner) to launch the container.  For data persistence, the container will mount the system directory TODO(`/home/{username}`) as the container's home directory.  We will eventually have TODO(`/home/{username}`) set up as an NFS mounted partition, so all the STEM camp students can easily share code.

This image expects to have a few environment variables set (see [dockerspawner](https://github.com/jupyterhub/dockerspawner)), so it may not run properly if you just do `docker run -it --rm data8-notebook`.  Running it from Jupyterhub should work, though you may need to remove the database `/srv/jupyterhub/jupyterhub.sqlite`.  TODO: I'm not sure what's causing the spawn failures here.


## Swarm Worker Instances
We manage the cluster with [Docker Swarm](https://docs.docker.com/engine/swarm/), which is integrated into Docker engine version 1.12 or greater.  The Docker Swarm manager node may be the same as the Jupyterhub node, in which case you shouldn't need to install any packages (item 2 below); however, the node must have the appropriate ports open (step 1 below), which aren't required for a plain Jupyterhub instance.  All the _worker_ nodes should still follow step 2 below to install Docker and start the daemon.

1. Create instance
   * For development, we're again using a t2.micro instance with an Amazon Linux AMI.  We set up a security group with the following rules to allow Docker Swarm to communicate.

    |Ports |	Protocol	| Source |
    |------|----------|--------|
    |22	| tcp	| 0.0.0.0/0, ::/0 |
    |2377	| tcp	| 0.0.0.0/0, ::/0 |
    |4789	| udp	| 0.0.0.0/0, ::/0 |
    |7946	| tcp	| 0.0.0.0/0, ::/0 |
    |7946	| udp	| 0.0.0.0/0, ::/0 |

2. Install packages
   SSH to your new instance and install some packages.
   ```bash
   sudo yum update
   sudo yum install docker git
   sudo service docker start
   sudo usermod -aG docker ec2-user
   ```

   Logout and SSH back in so we get in the docker group.

   ```bash
   cd ~/repos/NGC_...
   ./start.sh
   ```

3. Start a swarm manager
   This should print out something like:
   ```
   Swarm initialized: current node (dxn1zf6l61qsb1josjja83ngz) is now a manager.

   To add a worker to this swarm, run the following command:

       docker swarm join \
       --token SWMTKN-1-49nj1cmql0jkz5s954yi3oex3nedyz0fb0xx14ie39trti4wxv-8vxv8rssmk743ojnwacrr2e7c \
       192.168.99.100:2377

   To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
   ```

   We can get more info about the state of the swarm with `docker info` and more info about the nodes in the swarm with `docker node ls`.

4. Add worker nodes
   If we don't have the join command from initializing the manager, we can run `docker swarm join-token worker` on the manager node to get the join command again.

Leave the swarm with `docker swarm leave`.

Once we get everything set up and tested on at least one node, we can create an AMI to easily spawn more worker nodes.  We'll still have to SSH in and join them to the swarm, which shouldn't be a big deal.


## Swarm Manager Instances
Try using https://github.com/cassinyio/SwarmSpawner.git

```bash
cd && mkdir repos && cd repos
git clone https://github.com/cassinyio/SwarmSpawner.git
cd SwarmSpawner
sudo pip-3.4 install -r requirements.txt
sudo python3 setup.py install
```
Need to run jupyterhub inside a Docker service on the overlay network?

https://packages.debian.org/jessie-backports/docker.io





## Docker Swarm - Legacy
This works!  The standalone, legacy swarm is handled well by dockerspawner.*, so we'll use it instead of the relatively new
swarm mode built into the docker engine (at least until swarmspawner.SwarmSpawner is reliable).  I think the folks working on
dockerspawner are aware of the change, and are thinking about what to do to fix it.  For now, though, it looks like legacy
`docker run swarm ...` is the best way to go.

https://zonca.github.io/2016/05/jupyterhub-docker-swarm.html
http://jupyterhub.readthedocs.io/en/latest/getting-started.html#configuring-the-proxy-s-ip-address-and-port
https://docs.docker.com/swarm/overview/

Edit /etc/sysconfig/docker  OPTIONS="..." instead of what @andreazonca has.

We need a few extra ports open (2375, 4000, 8500, and 8888).  8888 is used by the hub API and needs to be open for incoming traffic for



`docker -H :4000 ps -a`


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


Need to have ports >= 32000 open on the worker nodes?  Need 8444 too?

I had a weird instance where a worker node dropped out of the swarm (all processes still running).
Maybe it lost the heartbeat?
I did a `docker restart {swarm_worker_container}`, but this got the jupyter container in a redirect loop.
I killed it with docker; can we do it form the admin panel of JHub?

We'll eventually save an AMI, I think.  Then we'll just have to SSH in and join the swarm.



## Kubernetes Cluster

https://kubernetes.io/docs/getting-started-guides/binary_release/
https://dl.k8s.io/v1.6.1/kubernetes-server-linux-amd64.tar.gz

https://kubernetes.io/docs/tasks/kubectl/install/
```bash
curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl

chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
```


### kops
https://kubernetes.io/docs/getting-started-guides/aws/
https://github.com/kubernetes/kops
https://github.com/kubernetes/kops/releases/tag/1.5.3
https://github.com/kubernetes/kops/blob/master/docs/aws.md


```bash
wget https://github.com/kubernetes/kops/releases/download/1.5.3/kops-linux-amd64
$ chmod +x kops-linux-amd64                 # Add execution permissions
$ mv kops-linux-amd64 /usr/local/bin/kops   # Move the kops to /usr/local/bin

sudo pip-3.4 install awscli

wget https://github.com/kubernetes/kubernetes/releases/download/v1.6.1/kubernetes.tar.gz

```


https://www.reancloud.com/blog/installing-kubernetes-using-kubeadm/

I had to disable gpg checks...
```bash
https://rpmfind.net/linux/rpm2html/search.php?query=iptables
yum --nogpgcheck localinstall iptables.arch.rpm

yum install kubeadm
```
Dang, still hanging on `kubeadm init`


## NFS Instance
TODO
