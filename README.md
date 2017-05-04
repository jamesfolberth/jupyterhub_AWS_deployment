# Jupyterhub on AWS
This is our configuration of Jupyterhub, Docker containers for Jupyter notebook instances, and NFS mounted home partitions for the [Northrop Grumman STEM Camp](https://conferencereg.colostate.edu/Registration/Welcome.aspx?e=EB64C01EC8135319E6CDA22A5B404146) - Data Science Track.
We'll have, say, 25 students who will use Jupyter notebooks in a week-long introduction to Data Science Summer camp.
Jupyterhub will start single-user Jupyter notebooks, spawned in Docker containers in a Docker Swarm on a small cluster of nodes in AWS.
For data sharing and persistence, we'll mount the user's home directories as an NFS partition, and point the home directory in the Docker containers to the NFS mount.

To see our deployment configuration and notes, see the `deploy` directory.

The notebooks we've written for the course are in `notebooks` directory.
