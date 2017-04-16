#!/bin/env bash

if [ -z "$PYTHONPATH" ]; then
   export PYTHONPATH=/home/ec2-user/jupyterhub/python/
else
   export PYTHONPATH=$PYTHONPATH:/home/ec2-user/jupyterhub/python/
fi

export EC2_PUBLIC_DNS=ec2-52-42-235-206.us-west-2.compute.amazonaws.com
export OAUTH_CALLBACK_URL=https://${EC2_PUBLIC_DNS}:8443/hub/oauth_callback

source /srv/jupyterhub/secret.env

jupyterhub -f config.py
