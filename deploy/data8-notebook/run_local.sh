#!/usr/bin/env bash

# Run our data8-notebook container locally.
# In the container, we use they jovyan user, but set the UID and GID to the
# current system user's UID and GID, so that when jovyan makes/edits files in
# the container, they appear to be from the system user.  We also mount the
# base path of the repo as the home directory in the container.

user=$USER
uid=`id -u $USER`
gid=`id -g $USER`
repo_base=`realpath \`pwd\`/../..`
notebook_base=$repo_base/notebooks

if [[ $EUID -eq 0 ]]; then
    echo "Don't run this script as root.  Add your personal user to the docker group and run with your personal user." 1>&2
    exit 1
fi

docker run -it --rm -e USER=$user -e NB_UID=$uid -e NB_GID=$gid -e HOME=$HOME \
  -p 8888:8888\
  --volume $notebook_base:/home/notebooks\
  data8-notebook $1

