#!/bin/env bash
#docker run -it --rm -e USER=testuser -e USER_ID=1001 -e HOME=/home/testuser \
#  --volume /home/testuser:/home/testuser \
#  data8-notebook $@
docker run -it --rm -e USER=jamesfolberth -e USER_ID=501 -e HOME=/home \
  --volume /mnt/nfs/home:/home\
  data8-notebook $@
#docker run -it --rm -e USER=testuser -e USER_ID=10000 -e HOME=/home \
#  data8-notebook $@
