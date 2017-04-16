# Configuration of Jupyterhub on AWS
This is our configuration of Jupyterhub, Docker containers for Jupyter notebook instances, and NFS mounted home partitions for the [Northrop Grumman STEM Camp](https://conferencereg.colostate.edu/Registration/Welcome.aspx?e=EB64C01EC8135319E6CDA22A5B404146) - Data Science Track.
We'll have, say, 25 students who will use Jupyter notebooks in a week-long Introductiont to Data Science Summer camp.
The plan is to have Jupyterhub start single-user Jupyter notebooks, which are spawned in Docker containers.
We'll have Docker Swarm start up the containers on one of a few worker nodes.
For data sharing and persistence, we'll mount the user's home directories as an NFS partition, and point the home directory in the Docker containers to the NFS mount.

## Jupyterhub Node
We followed most of the instructions from [Deploying Jupyterhub on AWS](https://github.com/jupyterhub/jupyterhub/wiki/Deploying-JupyterHub-on-AWS).
We deviate in a number of ways, however, since we have not registered a domain name.

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

2. Initial Setup 
   * To connect to the new instance, you'll need your SSH key (if it's your first time, you'll need AWS to generate one for you).
   Once you've downloaded your AWS SSH key and started up your instance, you can connect to it with `ssh -i ~/.ssh/aws_key.pem ec2-user@{PUBLIC_IPv4}`.
   The standard user is `ec2-user`, which has `sudo` privileges; once inside, you can make new users if you prefer.
   * Make a directory for Jupyterhub server files (e.g., SSL certs, user list)
    ```
    sudo mkdir /srv/jupyterhub
    sudo chown -R ec2-user:ec2-user /srv/jupyterhub/
    ```
   * Add `ec2-user` to the Docker group, so we don't have to `sudo` every time we want to run a Docker container.
    This is useful for testing things out.
    ```
    sudo usermod -aG docker ec2-user
    ```

3. 


## Jupyter Notebook Docker Containers
TODO

## Jupyter Notebook Worker Nodes
TODO

## NFS Node
TODO
