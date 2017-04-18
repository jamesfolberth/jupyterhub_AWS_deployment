# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
FROM jupyterhub/jupyterhub

MAINTAINER James Folberth <jamesfolberth@gmail.com>

# Install dockerspawner and its dependencies
RUN /opt/conda/bin/pip install \
    oauthenticator==0.5.* \
    dockerspawner==0.5.* \
    jupyter 

# Install docker on the jupyterhub container
RUN wget https://get.docker.com -q -O /tmp/getdocker && \
    chmod +x /tmp/getdocker && \
    sh /tmp/getdocker

# Clone and install SwarmSpawner
RUN cd ~ && mkdir repos && cd repos && \
    git clone https://github.com/cassinyio/SwarmSpawner.git && \
    cd SwarmSpawner && pip install -r requirements.txt && \
    python setup.py install

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

CMD ["/bin/bash", "/srv/jupyterhub/run_hub.sh"]
