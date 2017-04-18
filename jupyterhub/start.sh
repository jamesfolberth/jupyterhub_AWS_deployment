#!/bin/env bash

CWD=`pwd`
if [ -z "$PYTHONPATH" ]; then
   export PYTHONPATH=$CWD/python/
else
   export PYTHONPATH=$PYTHONPATH:$CWD/python/
fi

# Check existence of hub env vars file
HUB_ENV_FILE=/srv/jupyterhub/env
if [ -e $HUB_ENV_FILE ]; then
   source /srv/jupyterhub/env
else
   echo "Error: Jupyterhub environment variables file not found in $HUB_ENV_FILE" 1>&2
   exit 1
fi

# Check that we got the vars we want
vars="OAUTH_CLIENT_ID OAUTH_CLIENT_SECRET"
for var in $vars; do
   if [ -z ${!var} ]; then # "indirect parameter expansion"
      echo "Error: Variable $var is not set" 1>&2
      exit 1
   fi
done

# Get the public hostname
export EC2_PUBLIC_HOSTNAME=`ec2-metadata --public-hostname | sed -ne 's/public-hostname: //p'`
if [ -z $EC2_PUBLIC_HOSTNAME ]; then
   echo "Error: Failed to get EC2 public hostname from `ec2-metadata`"
   exit 1
else
   echo "Using EC2_PUBLIC_HOSTNAME=$EC2_PUBLIC_HOSTNAME"
fi
export OAUTH_CALLBACK_URL=https://${EC2_PUBLIC_HOSTNAME}:8443/hub/oauth_callback

# -E preserves environment variables (except not PATH, PYTHONPATH, etc.)
jhub_bin=`which jupyterhub`
sudo -E PYTHONPATH=$PYTHONPATH $jhub_bin -f config.py --debug
