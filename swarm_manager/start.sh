#!/bin/env bash

# Get the local IP for this EC2 instance
local_ip=`ec2-metadata --local-ipv4 | sed -ne 's/local-ipv4: //p'`

# Start up the swarm manager
#docker swarm init --advertise-addr $local_ip:2377 --listen-addr $local_ip:2377
#docker swarm init --advertise-addr $local_ip:2377
docker swarm init 

# Create an overlay network named "hubnet"
docker network create -d overlay --opt encrypted hubnet

