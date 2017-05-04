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

TODO: point to various repos with similar things (e.g., Jess Hamrick's stuff)
TODO: put README sections in the corresponding repos?

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

3a. Generate a self-signed SSL certificate.
   * If you don't have a domain name for the project, you can use a self-signed SSL certificate.
     A self-signed cert is quite okay for testing/development, but your browser will probably warn you about the cert when you navigate to your page.
     ```bash
     sudo mkdir /srv/jupyterhub/ssl
     sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /srv/jupyterhub/ssl/hub.key -out /srv/jupyterhub/ssl/hub.crt
     ```

3b. Set up nginx and SSL certificate
   * Let's now assume that we have a domain name, say `jamesfolberth.org`.
     We'll set up nginx to serve static HTML pages on `jamesfolberth.org`, and we'll set up Jupyterhub on `hub.jamesfolberth.org`.

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

    Certbot is included in the EPEL repos.
    https://aws.amazon.com/premiumsupport/knowledge-center/ec2-enable-epel/
    ```bash
    sudo yum-config-manager --enable epel
    ```

    https://certbot.eff.org/#centosrhel6-nginx
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

   See our config files in the `nginx` dirctory.

4. Register the project with Google OAuth 2.0
   * Note that each time we spin up a new AMI, it will (almost surely) get a new IP address.  We can buy an elastic IP, but for the purposes of development, we'll just have to update the IP and URIs below each time we spin up a new hub instance.

   * We want to use Google's authentication system for our project.  A lot of Jupyterhub deployments use GitHub authentication, which is good for their use-case, but for us, Google is probably simpler.
     Specificaly, we want to create an OAuth 2.0 Client ID for our project, so the users can authenticate with their Google accounts.
     Go to [Google API Manager](https://console.developers.google.com/apis/credentials) to set up a project.
     You'll need to set a meaningful project name, and get the domain name of your AWS hub instance (might be something like https://ec2-{IPv4ADDR}.us-west-2.compute.amazonaws.com if you aren't using your own domain).
     For us, we're going to be serving the hub from `hub.jamesfolberth.org`, but if you're not using your own domain, you would use something like `https://ec2-{IPv4ADDR}.us-west-2.compute.amazonaws.com`.
     If you're using the EC2 public hostname, you'll have to update the credentials every time the public hostname changes (e.g., when you start and stop the instance).

     Then set the authorized JS origins and callback URI:
     ```
     Authorized JavaScript origins:
         https://hub.jamesfolberth.org:443
     Authorized callback URIs:
         https://hub.jamesfolberth.org:443/hub/oauth_callback
     ```

     The callback /hub/oauth_callback is just what we assign to `OAUTH_CALLBACK_URL` in `start.sh`.
     If you're using the EC2 public hostname, you can use the following in `start.sh` to set `OAUTH_CALLBACK_URL` to the current instance's public hostname (behind port 8443).

     ```bash
     # Get the public hostname
     export EC2_PUBLIC_HOSTNAME=`ec2-metadata --public-hostname | sed -ne 's/public-hostname: //p'`
     if [ -z $EC2_PUBLIC_HOSTNAME ]; then
        echo "Error: Failed to get EC2 public hostname from `ec2-metadata`"
        exit 1
     else
        echo "Using EC2_PUBLIC_HOSTNAME=$EC2_PUBLIC_HOSTNAME"
     fi
     export OAUTH_CALLBACK_URL=https://${EC2_PUBLIC_HOSTNAME}:8443/hub/oauth_callback
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

     TODO: need to make a script to add users to the system.  Should be run on all machines too (i.e., take in userlist as an argument) and check if user already exists.

     As currently configured, Jupyterhub will create system users with the names `user.name`, `admin.user`, etc., and appropriate home directories.  `admin.user` won't have any special permissions on the underlying host system, but will be able to manage user notebook servers from Jupyterhub.

   * Clone this repo on the Jupyterhub host. ### and copy contents to a deploy folder.
   ```bash
   cd && mkdir repos && cd repos
   git clone https://github.com/jamesfolberth/NGC_STEM_camp_AWS.git
   cd NGC_STEM_camp_AWS/jupyterhub
   ```


   * If you don't put nginx on the front end, you can optionally NAT port 443 to 8443 to be served by the hub.
     You'll need to set `c.JupyterHub.port = 8443` in your `config.py`.
     We'll be using nginx, so we don't do this.
     ```bash
     sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to 8443
     ```

   * At this point, we haven't yet built Docker containers for the notebook instances, but we can still test out the hub a bit.  Start up the hub with `./start.sh`, which will set up a few environment variables and then run `sudo jupyterhub`.  The script uses `ec2-metadata` to get the running instance's public hostname.

     Point your browser to the hub (`https://{PUBLIC_IPv4ADDR}:8443` if you didn't use your own domain).
     If you're using a self-signed SSL cert, you'll see a warning that the connection is untrusted.
     You should see a Google authentication page, which, once authenticated, will pass you to the main Jupyterhub page, where you can start a server, view the control panel, etc.

     Since we haven't built the notebook server Docker containers, clicking "Start My Server" should error out (500).
     If we didn't authenticate properly (perhaps the email in `/srv/jupyterhub/userlist` is misspelled), you'll see an error 403.


## Jupyter Notebook Server Docker Container
We've combined what we like from a few Jupyter notebook docker containers, and merged them into one.  We've used code from Jupyter's [minimal-notebook](https://github.com/jupyter/docker-stacks/tree/master/minimal-notebook), [scipy-notebook](https://github.com/jupyter/docker-stacks/tree/master/scipy-notebook), and from Jupyterhub's [systemuser](https://github.com/jupyterhub/dockerspawner/tree/master/systemuser).

In the `data8-notebook` directory, there is a `Dockerfile`, and a few helper files.  We use Jupyter's [minimal-notebook](https://github.com/jupyter/docker-stacks/tree/master/minimal-notebook) as a base, then install [Anaconda](https://www.continuum.io/downloads) Python 3 and a variety of conda packages.  There are a few other little tweaks included from [scipy-notebook](https://github.com/jupyter/docker-stacks/tree/master/scipy-notebook).  Finally, we run the Jupyterhub single user notebook server a la [systemuser](https://github.com/jupyterhub/dockerspawner/tree/master/systemuser).

To build the image,
```bash
cd data8-notebook && ./build.sh
```
This will build the Docker image and give it the tag `data8-notebook`.  The Jupyterhub config `jupyterhub/confg.py` will use SystemUserSpawner from [dockerspawner](https://github.com/jupyterhub/dockerspawner) to launch the container.  For data persistence, the container will mount the system directory TODO(`/home/{username}`) as the container's home directory.  We will eventually have TODO(`/home/{username}`) set up as an NFS mounted partition, so all the STEM camp students can easily share code.

This image expects to have a few environment variables set (see [dockerspawner](https://github.com/jupyterhub/dockerspawner)), so it may not run properly if you just do `docker run -it --rm data8-notebook`.  Running it from Jupyterhub should work, though you may need to remove the database `/srv/jupyterhub/jupyterhub.sqlite`.  TODO: I'm not sure what's causing the spawn failures here.


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


Need to have ports >= 32000 open on the worker nodes?  Need 8444 too?
https://github.com/jupyterhub/jupyterhub/blob/master/docs/source/jupyterhub-aws-setup.md

I had a weird instance where a worker node dropped out of the swarm (all processes still running).
Maybe it lost the heartbeat?
I did a `docker restart {swarm_worker_container}`, but this got the jupyter container in a redirect loop.
I killed it with docker; can we do it form the admin panel of JHub?

We'll eventually save an AMI, I think.  Then we'll just have to SSH in and join the swarm.


## NFS Instance
TODO
