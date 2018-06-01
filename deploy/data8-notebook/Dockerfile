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

# Install Python 3 packages
# Remove pyqt and qt pulled in for matplotlib since we're only ever going to
# use notebook-friendly backends in these images
RUN conda install --quiet --yes \
    'nomkl' \
    'ipywidgets' \
    'pandas' \
    'numexpr' \
    'matplotlib' \
    'scipy' \
    'tensorflow' \
    'keras' \
    'scikit-learn' \
    'scikit-image' && \
    conda remove --quiet --yes --force qt pyqt && \
    conda clean -tipsy

RUN cat /usr/bin/yes | pip install \
   datascience okpy easygui IPython pydotplus numpy

# Activate ipywidgets extension in the environment that runs the notebook server
RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix

# Import matplotlib the first time to build the font cache.
ENV XDG_CACHE_HOME /home/$NB_USER/.cache/
#TODO: fix for python3 naming
#RUN MPLBACKEND=Agg $CONDA_DIR/envs/python3/bin/python -c "import matplotlib.pyplot"

# Configure ipython kernel to use matplotlib inline backend by default
RUN mkdir -p $HOME/.ipython/profile_default/startup
COPY mplimporthook.py $HOME/.ipython/profile_default/startup/



COPY extra_repo.list /etc/apt/sources.list.d/
RUN apt-get update && \
    apt-get install -y --no-install-recommends protobuf-compiler

RUN cat /usr/bin/yes | pip install \
    Cython pillow lxml

# If we're interested in running the COCO metrics
#RUN mkdir /home/repos && cd /home/repos && \
#    git clone https://github.com/cocodataset/cocoapi.git && \
#    cd cocoapi/PythonAPI && \
#    make -j 4 &&\
#    TODO

#RUN mkdir /home/repos && cd /home/repos &&\
#    git clone https://github.com/tensorflow/models.git &&\
#    cd models/research &&\
#    protoc object_detection/protos/*.proto --python_out=. &&\
#    cp -r object_detection /opt/conda/lib/python3.6/site-packages

# before building `git clone https://github.com/tensorflow/models.git tf_models`
RUN mkdir -p /home/repos/tensorflow_models
COPY tensorflow_models /home/repos/tensorflow_models
RUN cd /home/repos/tensorflow_models/research &&\
    protoc object_detection/protos/*.proto --python_out=. &&\
    cp -r object_detection /opt/conda/lib/python3.6/site-packages

RUN chown -R $NB_UID /home/repos

RUN mkdir -p /data/FastText
COPY FastText/ /data/FastText

RUN chown -R $NB_UID /data

WORKDIR /home
#RUN rm -rf /home/jovyan
ENV SHELL /bin/bash

# we will map 0.0.0.0:32XXX->8888/tcp
EXPOSE 8888 


