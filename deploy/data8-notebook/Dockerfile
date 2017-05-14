# Docker file for Jupyter notebook for NGC STEM Camp notebook nodes
# Modified from https://github.com/jupyter/docker-stacks/blob/master/scipy-notebook/Dockerfile
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
FROM jupyter/minimal-notebook

MAINTAINER James Folberth <jamesfolberth@gmail.com>

USER root

# libav-tools for matplotlib anim
RUN apt-get update && \
    apt-get install -y --no-install-recommends libav-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER $NB_USER

# Install Python 3 packages
# Remove pyqt and qt pulled in for matplotlib since we're only ever going to
# use notebook-friendly backends in these images
RUN conda install --quiet --yes \
    'nomkl' \
    'ipywidgets=6.0*' \
    'pandas=0.19*' \
    'numexpr=2.6*' \
    'matplotlib=2.0*' \
    'scipy=0.19*' \
    'scikit-learn=0.18*' \
    'scikit-image=0.12*' && \
    conda remove --quiet --yes --force qt pyqt && \
    conda clean -tipsy

# Activate ipywidgets extension in the environment that runs the notebook server
RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix

# Import matplotlib the first time to build the font cache.
ENV XDG_CACHE_HOME /home/$NB_USER/.cache/
#TODO: fix for python3 naming
#RUN MPLBACKEND=Agg $CONDA_DIR/envs/python3/bin/python -c "import matplotlib.pyplot"

# Configure ipython kernel to use matplotlib inline backend by default
RUN mkdir -p $HOME/.ipython/profile_default/startup
COPY mplimporthook.py $HOME/.ipython/profile_default/startup/

# From https://github.com/jupyterhub/dockerspawner/blob/master/systemuser/Dockerfile
USER root

WORKDIR /home
RUN userdel jovyan && rm -rf /home/jovyan
ENV SHELL /bin/bash

#while waiting for PR in jupyter/docker-stacks, keep the same naming conventions
ADD systemuser.sh /usr/local/bin/start-systemuser.sh

#RUN mkdir /home/jamesfolberth
# we will map 0.0.0.0:32XXX->8888/tcp
EXPOSE 8888 

WORKDIR /
RUN rm -rf /home

# smoke test entrypoint
#RUN USER_ID=65000 USER=systemusertest HOME=/home/systemusertest sh /usr/local/bin/start-systemuser.sh -h && userdel systemusertest

CMD ["sh", "/usr/local/bin/start-systemuser.sh"]
