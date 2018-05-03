#!/usr/bin/env bash

# Get the local IP for this EC2 instance
local_ip=`ec2-metadata --local-ipv4 | sed -ne 's/local-ipv4: //p'`

#JMF: this doesn't seem to have an effect... change OPTIONS in /etc/sysconfig/docker
#export DOCKER_OPTS="-H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock"

echo docker run -d -p 8500:8500 --name=consul progrium/consul -server -bootstrap -advertise=$local_ip
docker run -d -p 8500:8500 --name=consul progrium/consul -server -bootstrap -advertise=$local_ip

echo docker run -d -p 4000:4000 swarm manage -H :4000 --replication --advertise $local_ip:4000 consul://$local_ip:8500
docker run -d -p 4000:4000 swarm manage -H :4000 --replication --advertise $local_ip:4000 consul://$local_ip:8500

