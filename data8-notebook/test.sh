#!/bin/env bash
docker run -it --rm -e USER=jamesfolberth -e USER_ID=501 -e HOME=/home/jamesfolberth \
  --volume /home/jamesfolberth:/home/jamesfolberth \
  data8-notebook $@
