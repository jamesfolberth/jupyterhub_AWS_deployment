#!/bin/bash

if [ -z "$PYTHONPATH" ]; then
   export PYTHONPATH=/srv/jupyterhub/python/
else
   export PYTHONPATH=$PYTHONPATH:/srv/jupyterhub/python/
fi

# -E preserves environment variables (except not PATH, PYTHONPATH, etc.)
#jhub_bin=`which jupyterhub`
#sudo -E PYTHONPATH=$PYTHONPATH $jhub_bin -f /srv/jupyterhub/config.py --debug
jupyterhub -f /srv/jupyterhub/config.py --debug
