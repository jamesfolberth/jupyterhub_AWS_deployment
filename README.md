# Configuration of Jupyterhub on AWS
This is our configuration of Jupyterhub, Docker containers for Jupyter notebook instances, and NFS mounted home partitions for the [Northrop Grumman STEM Camp](https://conferencereg.colostate.edu/Registration/Welcome.aspx?e=EB64C01EC8135319E6CDA22A5B404146) - Data Science Track.



## Jupyterhub Node
We followed most of the instructions from [Deploying Jupyterhub on AWS](https://github.com/jupyterhub/jupyterhub/wiki/Deploying-JupyterHub-on-AWS).
We deviate in a number of ways, however, since we have not registered a domain name.

We developed and tested the config files on a t2.micro instance.
For deployment, we'll probably want a larger instance for the hub.
We set the following inbound rules:

|Ports |	Protocol	| Source |	
|------|----------|--------|
|22	| tcp	| 0.0.0.0/0, ::/0 |	
|80	| tcp	| 0.0.0.0/0, ::/0 |	
|443	| tcp	| 0.0.0.0/0, ::/0 |	
|8443	| tcp	| 0.0.0.0/0, ::/0 |	



## Jupyter Notebook Docker Containers


## Jupyter Notebook Worker Nodes
TODO


## NFS Node
TODO


