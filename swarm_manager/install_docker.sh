#!/bin/env bash

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

yum update
yum install docker git
service docker start
usermod -aG docker ec2-user
