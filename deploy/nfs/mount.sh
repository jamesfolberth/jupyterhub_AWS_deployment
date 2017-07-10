#!/bin/env bash

if [ -z $1 ]; then
   echo "Error: Pass in local IP or DN of main NFS node (EFS) as first argument"
   exit 1
fi

mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 $1:/  /mnt/nfs/home
