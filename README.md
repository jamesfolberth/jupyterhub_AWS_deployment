**[Jupyterhub Instances](#jupyterhub-instance)** |
**[Docker Containers](#jupyter-notebook-docker-containers)** |
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
    |80	| tcp	| 0.0.0.0/0, ::/0 |
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


## Jupyter Notebook Docker Containers
TODO

## Jupyter Notebook Worker Instances
TODO

## NFS Instance
TODO
