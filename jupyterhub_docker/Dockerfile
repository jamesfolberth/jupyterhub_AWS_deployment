# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
FROM jupyterhub/jupyterhub

MAINTAINER James Folberth <jamesfolberth@gmail.com>

# Install dockerspawner and its dependencies
RUN /opt/conda/bin/pip install \
    oauthenticator \
    dockerspawner \
    jupyter \
    docker 

# Install docker on the jupyterhub container
#RUN wget https://get.docker.com -q -O /tmp/getdocker && \
#    chmod +x /tmp/getdocker && \
#    sh /tmp/getdocker
#RUN apt-get -y install \
#    apt-transport-https ca-certificates curl gnupg2 && \
#    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
#    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian jessie stable" && \
#    apt-get update && apt-get install docker-ce
# Why not just get it from the Debian repos?
RUN echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list && \
    apt-get -y update && apt-get -y install docker.io

# Clone and install SwarmSpawner
RUN cd ~ && mkdir repos && cd repos && \
    git clone https://github.com/cassinyio/SwarmSpawner.git && \
    cd SwarmSpawner \ #&& pip install -r requirements.txt && \
    python setup.py install

#TODO this is a hack.  Looks like docker-py and docker have a name clash
RUN /usr/bin/yes | pip uninstall docker docker-py docker-pycreds && pip install docker

# Copy SSL cert and userlist
RUN mkdir -p /srv/jupyterhub/ssl
ADD ./secret/ssl /srv/jupyterhub/ssl
ADD ./secret/userlist /srv/jupyterhub/userlist

# We use port 8443 for the hub
EXPOSE 8443

# Copy our OAuthenticator hack
ADD ./python /srv/jupyterhub/python

# Set permissions for /srv/... stuff
RUN chmod 700 /srv/jupyterhub && chmod 600 /srv/jupyterhub/ssl/* && \
    chmod 600 /srv/jupyterhub/userlist


# These will probably change often during dev, so they're at the bottom
# Copy Jupyterhub config + scripts
ADD ./run_hub.sh /srv/jupyterhub/run_hub.sh
ADD ./config.py /srv/jupyterhub/config.py

#CMD ["/bin/bash"]
CMD ["/bin/bash", "/srv/jupyterhub/run_hub.sh"]
