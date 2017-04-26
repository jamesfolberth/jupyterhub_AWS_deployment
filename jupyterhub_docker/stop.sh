#!/bin/env bash
docker service rm $(docker service ls -q)
