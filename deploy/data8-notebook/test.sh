#!/bin/env bash
docker run -it --rm -e USER=testuser -e USER_ID=1001 -e HOME=/home/testuser \
  --volume /home/testuser:/home/testuser \
  data8-notebook $@
