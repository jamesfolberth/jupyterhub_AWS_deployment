#!/bin/sh
set -e

#if getent passwd $USER_ID > /dev/null ; then
if getent passwd $USER > /dev/null ; then
  echo "$USER ($USER_ID) exists"
else
  echo "Creating user $USER ($USER_ID)"
  #useradd -u $USER_ID -s $SHELL $USER # $HOME needs to be bind mounted
  useradd --home-dir $HOME $USER # $HOME needs to be bind mounted
  chown -R $USER:$USER $HOME
fi

ls -lR /home

notebook_arg=""
if [ -n "${NOTEBOOK_DIR:+x}" ]
then
    notebook_arg="--notebook-dir=${NOTEBOOK_DIR} --debug"
fi

sudo -E PATH="${CONDA_DIR}/bin:$PATH" -u $USER $CONDA_DIR/bin/jupyterhub-singleuser \
  --port=8888 \
  --ip=0.0.0.0 \
  --user=$JPY_USER \
  --cookie-name=$JPY_COOKIE_NAME \
  --base-url=$JPY_BASE_URL \
  --hub-prefix=$JPY_HUB_PREFIX \
  --hub-api-url=$JPY_HUB_API_URL \
  ${notebook_arg} \
  $@
