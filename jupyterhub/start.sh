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
vars="EC2_PUBLIC_DNS OAUTH_CLIENT_ID OAUTH_CLIENT_SECRET"
for var in $vars; do
   if [ -z ${!var} ]; then # "indirect parameter expansion"
      echo "Error: Variable $var is not set" 1>&2
      exit 1
   fi
done

export OAUTH_CALLBACK_URL=https://${EC2_PUBLIC_DNS}:8443/hub/oauth_callback

jupyterhub -f config.py
