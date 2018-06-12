# Jupyterhub Instance

The Jupyterhub instance will run Jupyterhub behind nginx, which we will use as a proxy server.
It will also run the Docker Swarm manager (container), which will connect Jupyterhub to the worker nodes.
For now, let's get the server (an AWS EC2 instance) up and running, and install Jupyterhub.


1. Starting the hub/webserver/Swarm manager instance
   * We developed and tested the config files on a t2.micro instance.
     For deployment, we'll probably want a larger instance for the hub, especially if it will also run a few notebook containers.
     We used a standard 64-bit Amazon Linux AMI.
     It has a reasonable number of packages in the `yum` repo, and most of the rest of the software we use can be installed with `pip`.

     We're running all instances in the same AWS virtual private cloud (VPC).
     Suppose our VPC's IPv4 CIDR is 172.31.0.0/16.
     We create a security group called "Jupyterhub" with the following allowed ports to the outside world:

        |Ports |	Protocol	| Source |
        |------|----------------|--------|
        |22	   | tcp	| 0.0.0.0/0, ::/0 |
        |80	   | tcp	| 0.0.0.0/0, ::/0 |
        |443   | tcp	| 0.0.0.0/0, ::/0 |

    * For inside the VPC only, we add the following ports to allow the hub API and connect to the notebooks on remote nodes.

        |Ports |	Protocol	| Source |
        |------|----------|--------|
        |8081| tcp	| 172.31.0.0/16 |
        |32000-33000| tcp	| 172.31.0.0/16 |

        Later on we'll use this node as a Docker swarm manager, which will require a few more open ports inside the VPC.
        See [Docker Swarm manager and workers](../swarm_legacy/README.md) for details.

    * Since we're inside a VPC (i.e., closed off from the outside world except for the above ports), we can instead just enable all ports 0-65536 for 172.31.0.0/16, which is the CIDR of the default VPC.
      This is probably the most convenient route to take, so we won't have to worry about opening ports later.


2. Install a bunch of packages
   * To connect to the new instance, you'll need your SSH private key.
     AWS will make a keypair and give you the private key if you don't already have one.
     Once you've downloaded your AWS SSH key and started up your instance, you can connect to it with `ssh -i ~/.ssh/aws_key.pem ec2-user@{PUBLIC_IPv4}`.
     The standard user is `ec2-user`, which has `sudo` privileges; once inside, you can make new users and add other authorized SSH keys if you like.
     We'll use `ec2-user2` to orchestrate everything.

     **Protip**: add the following function/alias to your `.bashrc`, so you can `aws-ssh {PUBLIC_IPv4}`.
     If you have an elastic IP or a domain name to use, you can also edit your `~/.ssh/config`.
     ```bash
     aws-ssh() {
         ssh -i ~/.ssh/aws_key.pem ec2-user@$1
     }
     ```

   * Make a directory for Jupyterhub server files (e.g., SSL certs, user list)
      ```bash
      sudo mkdir -p /srv/jupyterhub
      sudo chown -R ec2-user:ec2-user /srv/jupyterhub/
      chmod -R 700 /srv/jupyterhub
      ```

   * Install a bunch of packages from the system repos.
      ```bash
      sudo yum update -y
      curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | sudo bash
      sudo yum install -y python36 python36-pip python36-devel git git-lfs docker gcc gcc-c++
      sudo service docker start
      ```

   * Clone this repo
      ```bash
      cd && mkdir repos && cd repos
      git clone https://github.com/jamesfolberth/jupyterhub_AWS_deployment.git
      ```

   * Add `ec2-user` to the Docker group, so we don't have to `sudo` every time we want to run a Docker container.
      ```bash
      sudo usermod -aG docker ec2-user
      ```

   * Logout and back in to make group changes for `ec2-user`.
     Verify changes with `groups`.

   * Verify docker works with `docker run hello-world`.

   * Download Node.js, which provides npm.
     You probably want to visit [nodejs.org](https://nodejs.org/en/download/) to get the latest LTS version.

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
     ```

   * Install [configurable-http-proxy](https://github.com/jupyterhub/configurable-http-proxy), which is needed by Jupyterhub.
     ```bash
     sudo npm install -g configurable-http-proxy
     ```

   * Install python packages with `pip`.
     ```bash
     sudo pip-3.6 install jupyterhub
     sudo pip-3.6 install --upgrade notebook
     sudo pip-3.6 install oauthenticator dockerspawner
     ```

TODO JMF 22 May 2018: move to nginx README

3. Generate an SSL certificate

   a. If you don't have a domain name to use, generate a self-signed SSL certificate.
      A self-signed cert is quite okay for testing/development, but your browser will probably warn you about the cert when you navigate to your page.

    ```bash
    sudo mkdir /srv/jupyterhub/ssl
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /srv/jupyterhub/ssl/hub.key -out /srv/jupyterhub/ssl/hub.crt
    ```

    b. If you do have a domain name to use, see the [README](../nginx/README.md) in the `nginx` directory to generate SSL/TLS certs using [Let's Encrypt](https://letsencrypt.org/), set up routing to the domain/subdomain you want to use, and install and configure `nginx` to serve static HTML and proxy to the hub.


TODO JMF 22 May 2018: move to nginx README

4. Register the project with Google OAuth 2.0

   We want to use Google's authentication system for our project.
   A lot of Jupyterhub deployments use GitHub authentication, which is good for their use-case (because their users likely already have GitHub accounts), but for us, Google is probably simpler.
   To do this, we want to create an OAuth 2.0 Client ID for our project, so the users can authenticate with their Google accounts.

   * Go to [Google API Manager](https://console.developers.google.com/apis/credentials), create a project, and create an OAuth client ID.
     You'll need to set a meaningful, recognizable project name, as it will be displayed to the users when they authenticate.

   * Set the authorized JS origins to `https://hub.example.com:443`, and the authorized callback URI to `https://hub.example.com:443/hub/oauth_callback`.

     - If you're using your own domain, set `OAUTH_CALLBACK_URL` in the Jupyterhub `start.sh` script.

     - If you're using the EC2 public hostname (something like `ec2-{PUBLIC_IPv4}.us-west-2.compute.amazonaws.com`) instead of your own domain, you can use the following in `start.sh` to automatically set `OAUTH_CALLBACK_URL` to the current instance's public hostname.
        Note that you may have to update the authorized JS origin and callback URI on [Google API Manager](https://console.developers.google.com/apis/credentials) every time you stop/start the instance, as the restarted instance may be assigned a new DNS name.

        ```bash
        # Get the public hostname
        export EC2_PUBLIC_HOSTNAME=`ec2-metadata --public-hostname | sed -ne 's/public-hostname: //p'`
        if [ -z $EC2_PUBLIC_HOSTNAME ]; then
            echo "Error: Failed to get EC2 public hostname from `ec2-metadata`"
            exit 1
        else
            echo "Using EC2_PUBLIC_HOSTNAME=$EC2_PUBLIC_HOSTNAME"
        fi
        export OAUTH_CALLBACK_URL=https://${EC2_PUBLIC_HOSTNAME}:443/hub/oauth_callback
        ```

   * Once you've created the project, copy the client ID and secret to the file `/srv/jupyterhub/env`.

     ```bash
     # Google OAuth 2.0
     export OAUTH_CLIENT_ID=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA.apps.googleusercontent.com
     export OAUTH_CLIENT_SECRET=BBBBBBBBBBBBBBBBBBBBB
     ```

     Note hat these are **secret**, and should not be pushed to a git repo or accessible for other users (hence the `chmod 700` when creating `/srv/jupyterhub` and why we source this file instead of hard-coding a config file in the repo).

5. Set up Jupyterhub
    * Add at least one admin user to `/srv/jupyterhub/userlist` with the following format
        ```
        user.name@gmail.com admin
        ```
      This user will add other users through the web interface.
      We have callbacks set up in `my_oauthenticator.py` that should automagically get things set up, which includes

      1. Creating a system user on the Jupyterhub machine
      2. Creating a home directory for that user on the NFS-mounted EFS (mounted on `/mnt/nfs/home`)
      3. `rsync`ing the notebooks from this repo into the user's home directory.

    * If you have the [nginx](../nginx/README.md) and the [NFS mount](../nfs/README.md) set up, you can try starting Jupyterhub.

      But...
      - if authentication failed (e.g., user not in `/srv/jupyterhub/userlist` or user not added through Jupyterhub web interface by admin user), you should see a 403 "Forbidden".
      - we haven't built/pulled the data8-notebook (see [data8-notebook README](../data8-notebook/README.md)) or started the Docker swarm manager/workers, so if you try to start a server, you should see a 500 "Internal Server Error".

6. Set up [nginx](../nginx/README.md), [NFS](../nfs/README.md), and set up the [Docker swarm](../swarm_legacy/README.md).

7. Start Jupyterhub

    This should be as simple as running `start.sh`.
    I like to run `start.sh` in a `screen` session so I can detach and logout of my SSH connection.
