# Jupyterhub Instance
1. Starting the hub VM
   * We developed and tested the config files on a t2.micro instance.
     For deployment, we'll probably want a larger instance for the hub, especially if it will also run a few notebook containers.
     We used a standard 64-bit Amazon Linux AMI.
     It has a reasonable number of packages in the `yum` repo, and most of the rest of the software we use can be installed with `pip`.

     We're running all instances in the same AWS virtual private cloud (VPC).
     Suppose our VPC's IPv4 CIDR is 172.31.0.0/16.
     We create a security group called "Jupyterhub" with the following allowed ports to the outside world:

    |Ports |	Protocol	| Source |
    |------|----------|--------|
    |22	| tcp	| 0.0.0.0/0, ::/0 |
    |80	| tcp	| 0.0.0.0/0, ::/0 |
    |443	| tcp	| 0.0.0.0/0, ::/0 |

     For inside the VPC only, we add the following ports to allow the hub API and connect to the notebooks on remote nodes.
     Since we're inside a VPC (i.e., closed off from the outside world except for the above ports), I think we could instead just enable all ports 0-65536 for 172.31.0.0/16.

    |Ports |	Protocol	| Source |
    |------|----------|--------|
    |8081| tcp	| 172.31.0.0/16 |
    |32000-33000| tcp	| 172.31.0.0/16 |

    Later on we'll use this node as a Docker swarm manager, which will require a few more open ports inside the VPC.
    See TODO for details.

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

3a. Generate a self-signed SSL certificate, if you don't have a domain name to use.
    A self-signed cert is quite okay for testing/development, but your browser will probably warn you about the cert when you navigate to your page.
    ```bash
    sudo mkdir /srv/jupyterhub/ssl
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /srv/jupyterhub/ssl/hub.key -out /srv/jupyterhub/ssl/hub.crt
    ```

3b. If you do have a domain to use, see the [README](../nginx/README.md) in the `nginx` directory to generate SSL/TLS certs using [Let's Encrypt](https://letsencrypt.org/), set up routing to your domain (and the subdomain `hub.example.com`), and install and configure `nginx` to serve static HTML and proxy to the hub.

4. Register the project with Google OAuth 2.0
   We want to use Google's authentication system for our project.
   A lot of Jupyterhub deployments use GitHub authentication, which is good for their use-case, but for us, Google is probably simpler.
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

   The callback /hub/oauth_callback is just what we assign to `OAUTH_CALLBACK_URL` in `start.sh`, which is in turn used by JHub.
   If you're using your own domain, edit the `OAUTH_CALLBACK_URL` environment variable in `start.sh` to use your domain.

   If you're using the EC2 public hostname instead of your own domain, you can use the following in `start.sh` to set `OAUTH_CALLBACK_URL` to the current instance's public hostname (say, behind port 8443).
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

   Once you've created the project, copy the client ID and secret to the file `/srv/jupyterhub/env`.
   ```bash
   # Google OAuth 2.0
   export OAUTH_CLIENT_ID=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA.apps.googleusercontent.com
   export OAUTH_CLIENT_SECRET=BBBBBBBBBBBBBBBBBBBBB
   ```
   Do note that these are <b>secret</b>, and should not be pushed to a git repo or accessible for other users (hence the `chmod 700` in the beginning).

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
