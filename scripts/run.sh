s#!/usr/bin/env bash
echo "Create network..."
docker network create cps-net

echo "Starting Philosoph 1..."
docker run -d --net=cps-net --name philosoph1 phil:0.1


