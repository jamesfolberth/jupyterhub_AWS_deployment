#!/bin/env bash

#JMF: this doesn't seem to have an effect... change OPTIONS in /etc/sysconfig/docker
#export DOCKER_OPTS="-H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock"

if [ -z $1 ]; then
   echo "Error: Pass in local ip of consul container host as first argument"
   exit 1
fi

# Get the local IP for this EC2 instance
local_ip=`ec2-metadata --local-ipv4 | sed -ne 's/local-ipv4: //p'`

echo docker run -d swarm join --advertise=$local_ip:2375 consul://$1:8500
docker run -d swarm join --advertise=$local_ip:2375 consul://$1:8500

