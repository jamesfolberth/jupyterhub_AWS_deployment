#!/bin/env bash
docker run -it --rm -e USER=jamesfolberth -e USER_ID=501 -e HOME=/home \
  --volume /mnt/nfs/home:/home\
  data8-notebook $@
