#!/usr/bin/env bash

# pull the latest image from hub.docker.com
docker pull jamesfolberth/data8-notebook

# tag it locally as data8-notebook
docker tag jamesfolberth/data8-notebook data8-notebook
