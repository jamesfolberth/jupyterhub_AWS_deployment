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

2. Install a bunch of packages
   * To connect to the new instance, you'll need your SSH key (if it's your first time, you'll need AWS to generate one for you).
     Once you've downloaded your AWS SSH key and started up your instance, you can connect to it with `ssh -i ~/.ssh/aws_key.pem ec2-user@{PUBLIC_IPv4}`.
      The standard user is `ec2-user`, which has `sudo` privileges; once inside, you can make new users if you prefer.
   * Make a directory for Jupyterhub server files (e.g., SSL certs, user list)
      ```
      sudo mkdir -p /srv/jupyterhub
      sudo chown -R ec2-user:ec2-user /srv/jupyterhub/
      ```
   * Add `ec2-user` to the Docker group, so we don't have to `sudo` every time we want to run a Docker container.
      This is useful for testing things out.
      ```
      sudo usermod -aG docker ec2-user
      ```
   * Install a bunch of packages from the system repos.
      ```
      sudo yum update
      sudo yum install python34 python34-pip python34-devel git docker gcc gcc-g++
      sudo service docker start
      ```

   * Logout and back in to make group changes for `ec2-user`.  Verify changes with `groups`.
   * Verify docker works with `docker run hello-world`.
   * Download Node.js and npm ([stackoverflow](http://stackoverflow.com/questions/20028996/how-to-install-node-binary-distribution-files-on-linux)).
     ```
     wget https://npmjs.org/install.sh
     chmod +x install.sh
     sudo ./install.sh
     ```
   * Install [configurable-http-proxy](https://github.com/jupyterhub/configurable-http-proxy).
     ```
     sudo npm install -g configurable-http-proxy
     ```
   * Install python packages with `pip`.
     ```
     sudo pip-3.4 install jupyterhub
     sudo pip-3.4 install --upgrade notebook #JMF: perhaps not necessary?
     sudo pip-3.4 install oauthenticator dockerspawner
     ```

3. Generate a self-signed SSL certificate.
   * We don't have a domain name for our project, so we'll use a self-signed SSL certificate for now.
     Also, a self-signed cert is quite okay for testing/development.
     ```
     sudo mkdir /srv/jupyerhub/
     sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /srv/jupyterhub/ssl/hub.key -out /srv/jupyterhub/ssl/hub.crt
     ```

4. Register the project with Google OAuth 2.0
   * We want to use Google's authentication system for our project.  A lot of Jupyterhub deployments use GitHub authentication, which is good for their use-case, but for us, Google is probably simpler.
     Specificaly, we want to create an OAuth 2.0 Client ID for our project, so the users can authenticate with their Google accounts.
     Go to [Google API Manager](https://console.developers.google.com/apis/credentials) to set up a project.
     You'll need to set a meaningful project name, and get the domain name of your AWS hub instance (might be something like https://ec2-52-42-235-206.us-west-2.compute.amazonaws.com).
     We'll be using port 8443 for the hub, as we may eventually use nginx as a port 443 front-end.
     Then set the authorized JS origins and callback URI:
     ```
     Authorized JavaScript origins:
         https://ec2-{IP4ADDR}.us-west-2.compute.amazonaws.com:8443
     Authorized callback URIs:
         https://ec2-{IP4ADDR}.us-west-2.compute.amazonaws.com:8443/hub/oauth_callback
     ```

   * Once you've created the project, copy the client ID and secret to the file `/srv/jupyterhub/secret.env`:
    ```
    # Google OAuth 2.0
    export OAUTH_CLIENT_ID=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA.apps.googleusercontent.com
    export OAUTH_CLIENT_SECRET=BBBBBBBBBBBBBBBBBBBBB
    ```
    Do note that these are secret, and should not be pushed to a git repo or accessible for other users.


## Jupyter Notebook Docker Containers
TODO

## Jupyter Notebook Worker Instances
TODO

## NFS Instance
TODO
